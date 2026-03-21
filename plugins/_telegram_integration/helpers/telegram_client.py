import os

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from helpers.errors import format_error
from helpers.print_style import PrintStyle

# Text messages

MAX_MESSAGE_LENGTH: int = 4096  # Telegram message length limit


async def send_text(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_to_message_id: int | None = None,
    parse_mode: str | None = None,
) -> int | None:
    """Send text message, splitting if too long. Returns last message_id or None on error."""
    try:
        chunks = _split_text(text, MAX_MESSAGE_LENGTH)
        last_msg_id = None
        for chunk in chunks:
            try:
                msg = await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    reply_to_message_id=reply_to_message_id,
                    parse_mode=parse_mode,
                )
                last_msg_id = msg.message_id
            except TelegramBadRequest:
                # Retry without markdown if parse fails
                msg = await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    reply_to_message_id=reply_to_message_id,
                    parse_mode=None,
                )
                last_msg_id = msg.message_id
        return last_msg_id
    except Exception as e:
        PrintStyle.error(f"Telegram send_text failed: {format_error(e)}")
        return None

# Files and images

async def send_file(
    bot: Bot,
    chat_id: int,
    file_path: str,
    caption: str = "",
    reply_to_message_id: int | None = None,
) -> int | None:
    """Send a file from local path. Returns message_id or None on error."""
    try:
        if not os.path.isfile(file_path):
            PrintStyle.error(f"Telegram: file not found: {file_path}")
            return None
        input_file = FSInputFile(file_path)
        msg = await bot.send_document(
            chat_id=chat_id,
            document=input_file,
            caption=caption[:1024] if caption else None,
            reply_to_message_id=reply_to_message_id,
        )
        return msg.message_id
    except Exception as e:
        PrintStyle.error(f"Telegram send_file failed: {format_error(e)}")
        return None


async def send_photo(
    bot: Bot,
    chat_id: int,
    photo_path: str,
    caption: str = "",
    reply_to_message_id: int | None = None,
) -> int | None:
    """Send a photo from local path. Returns message_id or None on error."""
    try:
        if not os.path.isfile(photo_path):
            PrintStyle.error(f"Telegram: photo not found: {photo_path}")
            return None
        input_file = FSInputFile(photo_path)
        msg = await bot.send_photo(
            chat_id=chat_id,
            photo=input_file,
            caption=caption[:1024] if caption else None,
            reply_to_message_id=reply_to_message_id,
        )
        return msg.message_id
    except Exception as e:
        PrintStyle.error(f"Telegram send_photo failed: {format_error(e)}")
        return None


# Inline keyboards

def build_inline_keyboard(
    buttons: list[list[dict]],
) -> InlineKeyboardMarkup:
    """Build inline keyboard from a list of rows.
    Each row is a list of dicts with keys: text, callback_data or url.
    """
    rows = []
    for row in buttons:
        row_buttons = []
        for btn in row:
            if "url" in btn:
                row_buttons.append(InlineKeyboardButton(
                    text=btn["text"], url=btn["url"],
                ))
            else:
                row_buttons.append(InlineKeyboardButton(
                    text=btn["text"],
                    callback_data=btn.get("callback_data", btn["text"]),
                ))
        rows.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_text_with_keyboard(
    bot: Bot,
    chat_id: int,
    text: str,
    buttons: list[list[dict]],
    reply_to_message_id: int | None = None,
) -> int | None:
    """Send text with inline keyboard buttons."""
    try:
        keyboard = build_inline_keyboard(buttons)
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            reply_to_message_id=reply_to_message_id,
        )
        return msg.message_id
    except Exception as e:
        PrintStyle.error(f"Telegram send_text_with_keyboard failed: {format_error(e)}")
        return None

# Typing indicator

async def send_typing(bot: Bot, chat_id: int):
    """Send 'typing...' action to chat."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

# File download

async def download_file(
    bot: Bot,
    file_id: str,
    destination: str,
) -> str | None:
    """Download a file by file_id to destination path. Returns path or None on error."""
    try:
        file = await bot.get_file(file_id)
        if not file.file_path:
            return None
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        await bot.download_file(file.file_path, destination)
        return destination
    except Exception as e:
        PrintStyle.error(f"Telegram download failed: {format_error(e)}")
        return None

# Helpers

def _split_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at newline
        split_at = text.rfind("\n", 0, max_len)
        if split_at < max_len // 2:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def is_image_file(path: str) -> bool:
    _, ext = os.path.splitext(path.lower())
    return ext in _IMAGE_EXTENSIONS
