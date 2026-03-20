import asyncio
from functools import partial
from typing import Any

from helpers.extension import Extension
from helpers.errors import format_error
from helpers.print_style import PrintStyle
from helpers import plugins


PLUGIN_NAME: str = "_telegram_integration"


class TelegramBotManager(Extension):

    async def execute(self, **kwargs: Any) -> None:
        from plugins._telegram_integration.helpers.bot_manager import (
            get_all_bots,
            create_bot,
            cache_bot_info,
            start_polling,
            setup_webhook,
            stop_bot,
        )
        from plugins._telegram_integration.helpers.handler import (
            handle_start,
            handle_clear,
            handle_message,
            handle_callback_query,
            cleanup_old_attachments,
        )

        cleanup_old_attachments()

        config = plugins.get_plugin_config(PLUGIN_NAME) or {}
        bots_cfg = config.get("bots", [])
        enabled_names = {
            b["name"] for b in bots_cfg if b.get("enabled") and b.get("name") and b.get("token")
        }

        running = get_all_bots()

        # Stop bots that are no longer enabled
        for name in list(running.keys()):
            if name not in enabled_names:
                await stop_bot(name)

        # Start new bots
        for bot_cfg in bots_cfg:
            name = bot_cfg.get("name", "")
            if not name or not bot_cfg.get("enabled") or not bot_cfg.get("token"):
                continue
            if name in running:
                inst = running[name]
                if inst.task and not inst.task.done():
                    continue  # already running

            try:
                # Create handler closures that capture bot_name and config
                _on_start = partial(_wrap_start, bot_name=name, bot_cfg=bot_cfg)
                _on_clear = partial(_wrap_clear, bot_name=name, bot_cfg=bot_cfg)
                _on_message = partial(_wrap_message, bot_name=name, bot_cfg=bot_cfg)
                _on_callback = partial(_wrap_callback, bot_name=name, bot_cfg=bot_cfg)

                instance = create_bot(
                    name=name,
                    token=bot_cfg["token"],
                    on_message=_on_message,
                    on_command_start=_on_start,
                    on_command_clear=_on_clear,
                    on_callback_query=_on_callback,
                    group_mode=bot_cfg.get("group_mode", "mention"),
                )

                await cache_bot_info(instance)

                mode = bot_cfg.get("mode", "polling")
                if mode == "webhook":
                    webhook_url = bot_cfg.get("webhook_url", "")
                    webhook_secret = bot_cfg.get("webhook_secret", "")
                    if webhook_url:
                        await setup_webhook(instance, webhook_url, webhook_secret)
                    else:
                        PrintStyle.error(
                            f"Telegram ({name}): webhook mode requires webhook_url"
                        )
                        continue
                else:
                    await start_polling(instance)

                PrintStyle.success(f"Telegram ({name}): bot started in {mode} mode")

            except Exception as e:
                PrintStyle.error(
                    f"Telegram ({name}): failed to start: {format_error(e)}"
                )

# Wrapper functions for aiogram handlers

async def _wrap_start(message, bot_name: str, bot_cfg: dict):
    from plugins._telegram_integration.helpers.handler import handle_start
    await handle_start(message, bot_name, bot_cfg)


async def _wrap_clear(message, bot_name: str, bot_cfg: dict):
    from plugins._telegram_integration.helpers.handler import handle_clear
    await handle_clear(message, bot_name, bot_cfg)


async def _wrap_message(message, bot_name: str, bot_cfg: dict):
    from plugins._telegram_integration.helpers.handler import handle_message
    await handle_message(message, bot_name, bot_cfg)


async def _wrap_callback(query, bot_name: str, bot_cfg: dict):
    from plugins._telegram_integration.helpers.handler import handle_callback_query
    await handle_callback_query(query, bot_name, bot_cfg)
