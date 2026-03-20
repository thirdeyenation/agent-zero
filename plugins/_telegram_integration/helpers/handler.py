import json
import os
import threading
import time
import uuid

from aiogram.types import Message as TgMessage, CallbackQuery

from agent import Agent, AgentContext, AgentContextType, UserMessage
from helpers import guids, plugins, files
from helpers import message_queue as mq
from helpers.notification import NotificationManager, NotificationType, NotificationPriority
from helpers.persist_chat import save_tmp_chat
from helpers.print_style import PrintStyle
from helpers.errors import format_error
from initialize import initialize_agent

from plugins._telegram_integration.helpers import telegram_client as tc
from plugins._telegram_integration.helpers.bot_manager import get_bot


PLUGIN_NAME = "_telegram_integration"
DOWNLOAD_FOLDER = "usr/telegram/attachments"
STATE_FILE = "usr/telegram/state.json"

# Context data keys
CTX_TG_BOT = "telegram_bot"
CTX_TG_CHAT_ID = "telegram_chat_id"
CTX_TG_USER_ID = "telegram_user_id"
CTX_TG_USERNAME = "telegram_username"
CTX_TG_LAST_MSG_ID = "telegram_last_msg_id"

# Transient
CTX_TG_ATTACHMENTS = "_telegram_response_attachments"
CTX_TG_KEYBOARD = "_telegram_response_keyboard"

# Chat mapping: (bot_name, tg_user_id) → AgentContext ID

_chat_map_lock = threading.Lock()


def _load_state() -> dict:
    path = files.get_abs_path(STATE_FILE)
    if os.path.isfile(path):
        try:
            return json.loads(files.read_file(path))
        except Exception:
            return {}
    return {}


def _save_state(state: dict):
    path = files.get_abs_path(STATE_FILE)
    files.make_dirs(path)
    files.write_file(path, json.dumps(state))


def _map_key(bot_name: str, user_id: int) -> str:
    return f"{bot_name}:{user_id}"


def cleanup_old_attachments():
    """Remove downloaded attachment files older than per-bot max age. 0 = keep forever."""
    config = plugins.get_plugin_config(PLUGIN_NAME) or {}
    bots_cfg = config.get("bots") or []
    total_removed = 0
    for bot_cfg in bots_cfg:
        bot_name = bot_cfg.get("name", "")
        if not bot_name:
            continue
        max_age_hours = bot_cfg.get("attachment_max_age_hours", 0)
        if not max_age_hours or max_age_hours <= 0:
            continue
        folder = os.path.join(files.get_abs_path(DOWNLOAD_FOLDER), bot_name)
        if not os.path.isdir(folder):
            continue
        cutoff = time.time() - max_age_hours * 3600
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            try:
                if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                    os.remove(path)
                    total_removed += 1
            except OSError:
                pass
    if total_removed:
        PrintStyle.info(f"Telegram: cleaned up {total_removed} old attachment(s)")

# Access control

def _is_allowed(bot_cfg: dict, user_id: int, username: str | None) -> bool:
    allowed = bot_cfg.get("allowed_users") or []
    if not allowed:
        return True  # empty = allow all
    for entry in allowed:
        entry_str = str(entry).strip()
        if entry_str.startswith("@"):
            if username and f"@{username}" == entry_str:
                return True
        else:
            try:
                if int(entry_str) == user_id:
                    return True
            except ValueError:
                if username and entry_str.lower() == username.lower():
                    return True
    return False


def _get_project(bot_cfg: dict, user_id: int) -> str:
    user_projects = bot_cfg.get("user_projects") or {}
    project = user_projects.get(str(user_id), "")
    if not project:
        project = bot_cfg.get("default_project", "")
    return project

# Message handlers (registered with aiogram by bot_manager)

async def handle_start(message: TgMessage, bot_name: str, bot_cfg: dict):
    """Handle /start command."""
    user = message.from_user
    if not user:
        return

    if not _is_allowed(bot_cfg, user.id, user.username):
        await message.reply("⛔ You are not authorized to use this bot.")
        return

    instance = get_bot(bot_name)
    if not instance:
        return

    await message.reply(
        f"👋 Hello {user.first_name}! I'm connected to Agent Zero.\n\n"
        "Send me a message and I'll process it.\n"
        "Use /clear to reset the conversation."
    )

    # Ensure a chat context exists
    await _get_or_create_context(bot_name, bot_cfg, message)


async def handle_clear(message: TgMessage, bot_name: str, bot_cfg: dict):
    """Handle /clear command — reset user's chat context."""
    user = message.from_user
    if not user:
        return

    if not _is_allowed(bot_cfg, user.id, user.username):
        return

    key = _map_key(bot_name, user.id)

    with _chat_map_lock:
        state = _load_state()
        ctx_id = state.get("chats", {}).get(key)
        if ctx_id:
            ctx = AgentContext.get(ctx_id)
            if ctx:
                ctx.reset()
                PrintStyle.info(f"Telegram ({bot_name}): cleared chat for user {user.id}")

    instance = get_bot(bot_name)
    if instance:
        await tc.send_text(
            instance.bot, message.chat.id,
            "🗑 Chat cleared. Send a new message to start fresh.",
            parse_mode=None,
        )

    # Send notification
    username_str = f"@{user.username}" if user.username else str(user.id)
    NotificationManager.send_notification(
        type=NotificationType.INFO,
        priority=NotificationPriority.NORMAL,
        title="Telegram: chat cleared",
        message=f"{username_str} cleared their chat via /clear",
        display_time=5,
        group="telegram",
    )


async def handle_message(message: TgMessage, bot_name: str, bot_cfg: dict):
    """Handle incoming user message."""
    user = message.from_user
    if not user:
        return

    if not _is_allowed(bot_cfg, user.id, user.username):
        return

    instance = get_bot(bot_name)
    if not instance:
        return

    # Send typing indicator
    await tc.send_typing(instance.bot, message.chat.id)

    # Get or create agent context
    context = await _get_or_create_context(bot_name, bot_cfg, message)
    if not context:
        await tc.send_text(
            instance.bot, message.chat.id,
            "❌ Failed to create chat session.",
            parse_mode=None,
        )
        return

    # Build user message text
    text = _extract_message_content(message)
    attachments = await _download_attachments(instance.bot, message, bot_name=bot_name)

    # Store last incoming message ID for reply threading
    context.data[CTX_TG_LAST_MSG_ID] = message.message_id

    # Build user message with prompt
    agent = context.agent0
    user_msg = agent.read_prompt(
        "fw.telegram.user_message.md",
        sender=_format_user(user),
        body=text,
    )

    instructions = bot_cfg.get("agent_instructions", "")
    if instructions:
        user_msg += agent.read_prompt(
            "fw.telegram.user_message_instructions.md",
            instructions=instructions,
        )

    system_ctx = agent.read_prompt("fw.telegram.system_context.md")

    mq.log_user_message(context, user_msg, attachments, source=" (telegram)")
    context.communicate(UserMessage(
        message=user_msg,
        system_message=[system_ctx],
        attachments=attachments,
    ))

    save_tmp_chat(context)

    # Send notification
    username_str = f"@{user.username}" if user.username else str(user.id)
    preview = (text[:80] + "...") if len(text) > 80 else text
    NotificationManager.send_notification(
        type=NotificationType.INFO,
        priority=NotificationPriority.HIGH,
        title="Telegram: new message",
        message=f"From {username_str}: {preview}",
        display_time=10,
        group="telegram",
    )


async def handle_callback_query(query: CallbackQuery, bot_name: str, bot_cfg: dict):
    """Handle inline keyboard button press."""
    user = query.from_user
    if not user or not query.message:
        return

    if not _is_allowed(bot_cfg, user.id, user.username):
        await query.answer("Not authorized.")
        return

    await query.answer()

    # Treat callback data as a user message
    text = query.data or ""
    if not text:
        return

    context = await _get_or_create_context_from_user(
        bot_name, bot_cfg, user.id, user.username, query.message.chat.id,
    )
    if not context:
        return

    agent = context.agent0
    user_msg = agent.read_prompt(
        "fw.telegram.user_message.md",
        sender=_format_user(user),
        body=f"[Button pressed: {text}]",
    )

    mq.log_user_message(context, user_msg, [], source=" (telegram)")
    context.communicate(UserMessage(message=user_msg))
    save_tmp_chat(context)

# Context management

async def _get_or_create_context(
    bot_name: str,
    bot_cfg: dict,
    message: TgMessage,
) -> AgentContext | None:
    user = message.from_user
    if not user:
        return None
    return await _get_or_create_context_from_user(
        bot_name, bot_cfg, user.id, user.username, message.chat.id,
    )


async def _get_or_create_context_from_user(
    bot_name: str,
    bot_cfg: dict,
    user_id: int,
    username: str | None,
    chat_id: int,
) -> AgentContext | None:
    key = _map_key(bot_name, user_id)

    with _chat_map_lock:
        state = _load_state()
        chats = state.setdefault("chats", {})
        ctx_id = chats.get(key)

        # Check if existing context is still alive
        if ctx_id:
            ctx = AgentContext.get(ctx_id)
            if ctx:
                return ctx
            # Context was garbage collected, remove stale mapping
            chats.pop(key, None)

        # Create new context
        try:
            config = initialize_agent()
            display_name = f"@{username}" if username else str(user_id)
            ctx = AgentContext(config, name=f"Telegram: {display_name}")

            ctx.data[CTX_TG_BOT] = bot_name
            ctx.data[CTX_TG_CHAT_ID] = chat_id
            ctx.data[CTX_TG_USER_ID] = user_id
            ctx.data[CTX_TG_USERNAME] = username or ""

            project = _get_project(bot_cfg, user_id)
            if project:
                from helpers import projects
                projects.activate_project(ctx.id, project)

            chats[key] = ctx.id
            _save_state(state)

            PrintStyle.success(
                f"Telegram ({bot_name}): new chat {ctx.id} for user {display_name}"
            )
            return ctx

        except Exception as e:
            PrintStyle.error(f"Telegram: failed to create context: {format_error(e)}")
            return None

# Message content extraction

def _extract_message_content(message: TgMessage) -> str:
    parts = []

    if message.text:
        parts.append(message.text)
    elif message.caption:
        parts.append(message.caption)

    if message.location:
        parts.append(f"[Location: {message.location.latitude}, {message.location.longitude}]")

    if message.contact:
        parts.append(
            f"[Contact: {message.contact.first_name} "
            f"{message.contact.last_name or ''} "
            f"phone={message.contact.phone_number}]"
        )

    if message.sticker:
        emoji = message.sticker.emoji or ""
        parts.append(f"[Sticker: {emoji}]")

    if message.voice:
        parts.append("[Voice message — see attachment]")

    if message.video_note:
        parts.append("[Video note — see attachment]")

    return "\n".join(parts) if parts else "[No text content]"


async def _download_attachments(bot, message: TgMessage, bot_name: str = "") -> list[str]:
    """Download photos, documents, audio, voice, video from message."""
    paths: list[str] = []
    sub = bot_name if bot_name else "_default"
    download_base = os.path.join(files.get_abs_path(DOWNLOAD_FOLDER), sub)
    os.makedirs(download_base, exist_ok=True)

    async def _dl(file_id: str, filename: str) -> str | None:
        dest = os.path.join(download_base, f"{uuid.uuid4().hex[:8]}_{filename}")
        return await tc.download_file(bot, file_id, dest)

    # Photo: get largest resolution
    if message.photo:
        photo = message.photo[-1]
        path = await _dl(photo.file_id, f"photo_{photo.file_unique_id}.jpg")
        if path:
            paths.append(path)

    # Document
    if message.document:
        fname = message.document.file_name or f"file_{message.document.file_unique_id}"
        path = await _dl(message.document.file_id, fname)
        if path:
            paths.append(path)

    # Audio
    if message.audio:
        fname = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
        path = await _dl(message.audio.file_id, fname)
        if path:
            paths.append(path)

    # Voice
    if message.voice:
        path = await _dl(message.voice.file_id, f"voice_{message.voice.file_unique_id}.ogg")
        if path:
            paths.append(path)

    # Video
    if message.video:
        fname = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        path = await _dl(message.video.file_id, fname)
        if path:
            paths.append(path)

    # Video note
    if message.video_note:
        path = await _dl(
            message.video_note.file_id,
            f"videonote_{message.video_note.file_unique_id}.mp4",
        )
        if path:
            paths.append(path)

    return paths

# Reply sending (called from process_chain_end extension)

async def send_telegram_reply(
    context: AgentContext,
    response_text: str,
    attachments: list[str] | None = None,
    keyboard: list[list[dict]] | None = None,
) -> str | None:
    """Send reply to Telegram user. Returns error string or None on success."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    bot_name = context.data.get(CTX_TG_BOT)
    if not bot_name:
        return "No Telegram bot configured on context"

    instance = get_bot(bot_name)
    if not instance:
        return f"Bot '{bot_name}' not running"

    chat_id = context.data.get(CTX_TG_CHAT_ID)
    if not chat_id:
        return "No chat_id on context"

    # Create a temporary Bot bound to the current event loop to avoid
    # cross-event-loop issues with the shared instance's aiohttp session.
    reply_bot = Bot(
        token=instance.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    try:
        # Send attachments first
        if attachments:
            for path in attachments:
                if tc.is_image_file(path):
                    await tc.send_photo(reply_bot, chat_id, path)
                else:
                    await tc.send_file(reply_bot, chat_id, path)

        # Send text (with or without keyboard)
        if response_text:
            if keyboard:
                await tc.send_text_with_keyboard(
                    reply_bot, chat_id, response_text, keyboard,
                )
            else:
                await tc.send_text(reply_bot, chat_id, response_text)

        return None

    except Exception as e:
        error = format_error(e)
        PrintStyle.error(f"Telegram reply failed: {error}")
        return error
    finally:
        await reply_bot.session.close()

# Helpers

def _format_user(user) -> str:
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    if user.username:
        name += f" (@{user.username})"
    return name.strip() or str(user.id)


def find_context_for_bot_chat(bot_name: str, chat_id: int) -> AgentContext | None:
    """Find active context matching a Telegram bot + chat_id."""
    for ctx in AgentContext.all():
        if ctx.data.get(CTX_TG_BOT) == bot_name and ctx.data.get(CTX_TG_CHAT_ID) == chat_id:
            return ctx
    return None
