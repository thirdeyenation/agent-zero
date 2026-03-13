import asyncio

from crontab import CronTab

from helpers.extension import Extension
from helpers.errors import format_error
from helpers.print_style import PrintStyle
from helpers import plugins


PLUGIN_NAME = "_email_integration"
DEFAULT_INTERVAL = 15
MIN_INTERVAL = 5

_poll_tasks: dict[str, asyncio.Task] = {}


def _get_sleep_seconds(handler_cfg: dict) -> float:
    mode = handler_cfg.get("poll_mode", "seconds")
    if mode == "cron":
        expr = handler_cfg.get("poll_interval_cron", "*/2 * * * *")
        try:
            return max(CronTab(expr).next(default_utc=True), MIN_INTERVAL)
        except Exception:
            return DEFAULT_INTERVAL
    return max(handler_cfg.get("poll_interval_seconds", DEFAULT_INTERVAL), MIN_INTERVAL)


async def _handler_poll_loop(handler_name: str):
    from plugins._email_integration.helpers.handler import (
        _poll_single_handler,
        _load_state,
        _save_state,
        _state_lock,
    )

    while True:
        config = plugins.get_plugin_config(PLUGIN_NAME) or {}
        handlers = config.get("handlers", [])
        handler_cfg = next(
            (h for h in handlers if h.get("name") == handler_name and h.get("enabled")),
            None,
        )
        if handler_cfg is None:
            break

        try:
            async with _state_lock:
                state = _load_state()
                await _poll_single_handler(handler_cfg, state)
                _save_state(state)
        except Exception as e:
            PrintStyle.error(f"Email poll error ({handler_name}): {format_error(e)}")

        sleep_sec = _get_sleep_seconds(handler_cfg)
        await asyncio.sleep(sleep_sec)


class EmailAutoPoll(Extension):

    async def execute(self, **kwargs):
        config = plugins.get_plugin_config(PLUGIN_NAME) or {}
        handlers = config.get("handlers", [])
        enabled_names = {
            h["name"] for h in handlers if h.get("enabled") and h.get("name")
        }

        for name in list(_poll_tasks):
            if name not in enabled_names or _poll_tasks[name].done():
                task = _poll_tasks.pop(name, None)
                if task and not task.done():
                    task.cancel()

        for name in enabled_names:
            if name not in _poll_tasks or _poll_tasks[name].done():
                _poll_tasks[name] = asyncio.create_task(_handler_poll_loop(name))
