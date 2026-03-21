import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from helpers.errors import format_error
from helpers.print_style import PrintStyle

# Data models

@dataclass
class BotInstance:
    name: str
    bot: Bot
    dispatcher: Dispatcher
    router: Router
    task: asyncio.Task | None = None  # polling task
    webhook_app: object | None = None  # aiohttp app for webhook mode
    bot_info: object | None = None  # cached result of bot.get_me()

# Bot registry (singleton, persists across module reloads)

_bots: dict[str, BotInstance] = {}


def get_bot(name: str) -> BotInstance | None:
    return _bots.get(name)


def get_all_bots() -> dict[str, BotInstance]:
    return _bots

# Bot creation

def create_bot(
    name: str,
    token: str,
    on_message: Callable[..., Awaitable],
    on_command_start: Callable[..., Awaitable],
    on_command_clear: Callable[..., Awaitable],
    on_callback_query: Callable[..., Awaitable] | None = None,
    group_mode: str = "mention",
) -> BotInstance:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()
    router = Router()

    # Register command handlers
    router.message.register(on_command_start, CommandStart())
    router.message.register(on_command_clear, Command("clear"))

    if on_callback_query:
        router.callback_query.register(on_callback_query)

    # Register message handler with group filtering
    if group_mode == "off":
        # Private chats only
        router.message.register(
            on_message, F.chat.type == ChatType.PRIVATE,
        )
    elif group_mode == "mention":
        # Private chats: all messages; Groups: only when mentioned/replied
        router.message.register(
            on_message, F.chat.type == ChatType.PRIVATE,
        )
        router.message.register(
            _make_group_mention_filter(on_message, bot),
        )
    else:
        # All messages in all chats
        router.message.register(on_message)

    dp.include_router(router)
    instance = BotInstance(name=name, bot=bot, dispatcher=dp, router=router)
    _bots[name] = instance
    return instance


async def cache_bot_info(instance: BotInstance):
    """Fetch and cache bot info. Call after create_bot."""
    if not instance.bot_info:
        instance.bot_info = await instance.bot.get_me()
    return instance.bot_info


def _make_group_mention_filter(handler: Callable, bot: Bot):
    """Create a group message handler that only responds to mentions and replies."""
    async def _group_handler(message: Message):
        if message.chat.type == ChatType.PRIVATE:
            return
        # Use cached bot_info from the instance
        bot_info = None
        for b in _bots.values():
            if b.bot is bot:
                bot_info = b.bot_info
                break
        if not bot_info:
            bot_info = await bot.get_me()
        bot_username = bot_info.username or ""

        # Check for reply to bot
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == bot_info.id:
                await handler(message)
                return

        # Check for @mention in text
        if message.text and f"@{bot_username}" in message.text:
            await handler(message)
            return

        # Check entities for mention
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    if mention_text.lower() == f"@{bot_username.lower()}":
                        await handler(message)
                        return

    _group_handler.__name__ = f"_group_handler_{id(handler)}"
    return _group_handler

# Polling

async def start_polling(instance: BotInstance) -> asyncio.Task:
    async def _poll():
        try:
            PrintStyle.info(f"Telegram ({instance.name}): starting polling")
            await instance.dispatcher.start_polling(
                instance.bot,
                handle_signals=False,
            )
        except asyncio.CancelledError:
            PrintStyle.info(f"Telegram ({instance.name}): polling cancelled")
        except Exception as e:
            PrintStyle.error(f"Telegram ({instance.name}): polling error: {format_error(e)}")

    task = asyncio.create_task(_poll())
    instance.task = task
    return task


async def stop_polling(instance: BotInstance):
    if instance.task and not instance.task.done():
        await instance.dispatcher.stop_polling()
        instance.task.cancel()
        try:
            await instance.task
        except asyncio.CancelledError:
            pass
    instance.task = None

# Webhook

async def setup_webhook(instance: BotInstance, url: str, secret: str = ""):
    """Set Telegram webhook and return aiohttp app for local serving."""
    from aiohttp import web

    await instance.bot.set_webhook(
        url=url,
        secret_token=secret or None,
    )

    app = web.Application()
    handler = SimpleRequestHandler(
        dispatcher=instance.dispatcher,
        bot=instance.bot,
        secret_token=secret or None,
    )
    handler.register(app, path=f"/telegram/{instance.name}")
    instance.webhook_app = app
    PrintStyle.info(f"Telegram ({instance.name}): webhook set to {url}")
    return app


async def remove_webhook(instance: BotInstance):
    try:
        await instance.bot.delete_webhook()
    except Exception as e:
        PrintStyle.error(f"Telegram ({instance.name}): remove webhook error: {format_error(e)}")

# Cleanup

async def stop_bot(name: str):
    instance = _bots.pop(name, None)
    if not instance:
        return
    if instance.task and not instance.task.done():
        await stop_polling(instance)
    else:
        await remove_webhook(instance)
    try:
        await instance.bot.session.close()
    except Exception:
        pass
    PrintStyle.info(f"Telegram ({name}): stopped")


# Test connection

async def test_token(token: str) -> tuple[bool, str]:
    try:
        bot = Bot(token=token)
        info = await bot.get_me()
        await bot.session.close()
        return True, f"Connected as @{info.username} ({info.first_name})"
    except Exception as e:
        return False, format_error(e)
