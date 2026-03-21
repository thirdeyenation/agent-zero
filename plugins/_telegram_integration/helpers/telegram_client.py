import os
import re

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from helpers.errors import format_error
from helpers.print_style import PrintStyle

_UNSET = object()  # sentinel: "not provided" (lets Bot default apply)

# Text messages

MAX_MESSAGE_LENGTH: int = 4096  # Telegram message length limit


async def send_text(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_to_message_id: int | None = None,
    parse_mode: object = _UNSET,
) -> int | None:
    """Send text message, splitting if too long. Returns last message_id or None on error.

    parse_mode behaviour:
      - _UNSET (default): omitted from send_message → Bot's DefaultBotProperties applies.
      - None: explicitly no formatting.
      - "HTML"/"Markdown"/etc.: that specific mode.
    """
    try:
        chunks = _split_text(text, MAX_MESSAGE_LENGTH)
        last_msg_id = None
        pm_kwargs: dict = {} if parse_mode is _UNSET else {"parse_mode": parse_mode}
        for chunk in chunks:
            try:
                msg = await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    reply_to_message_id=reply_to_message_id,
                    **pm_kwargs,
                )
                last_msg_id = msg.message_id
            except TelegramBadRequest:
                # Retry as plain text, stripping HTML tags
                plain = re.sub(r"<[^>]+>", "", chunk)
                msg = await bot.send_message(
                    chat_id=chat_id,
                    text=plain,
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
    parse_mode: object = _UNSET,
) -> int | None:
    """Send text with inline keyboard buttons."""
    try:
        keyboard = build_inline_keyboard(buttons)
        pm_kwargs: dict = {} if parse_mode is _UNSET else {"parse_mode": parse_mode}
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            reply_to_message_id=reply_to_message_id,
            **pm_kwargs,
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
        if split_at == -1 or split_at < max_len // 2:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def is_image_file(path: str) -> bool:
    _, ext = os.path.splitext(path.lower())
    return ext in _IMAGE_EXTENSIONS


def md_to_telegram_html(text: str) -> str:
    """Convert standard Markdown to Telegram-compatible HTML.

    Handles: fenced code blocks, inline code, bold, italic, strikethrough,
    links, headings, blockquotes, tables, and nested lists.
    """
    stash: list[str] = []

    def _put(html: str) -> str:
        stash.append(html)
        return f"\x00B{len(stash) - 1}\x00"

    def _esc(t: str) -> str:
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Stash fenced code blocks
    def _code_block(m: re.Match) -> str:
        lang, code = m.group(1) or "", _esc(m.group(2))
        tag = f'<pre><code class="language-{lang}">{code}</code></pre>' if lang else f"<pre>{code}</pre>"
        return _put(tag)

    text = re.sub(r"```(\w*)\n(.*?)```", _code_block, text, flags=re.DOTALL)

    # Stash inline code
    text = re.sub(r"`([^`]+)`", lambda m: _put(f"<code>{_esc(m.group(1))}</code>"), text)

    # Stash Markdown tables as list-style text
    text = _stash_tables(text, _put, _esc)

    # Escape remaining HTML chars
    text = _esc(text)

    # Inline formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)\*([^*]+?)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\w)_([^_]+?)_(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"^#{1,6}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)

    # Blockquotes: > text → <blockquote>
    text = _convert_blockquotes(text)

    # Lists (nested + ordered)
    text = _convert_lists(text)

    # Restore all stashed blocks
    for i, block in enumerate(stash):
        text = text.replace(f"\x00B{i}\x00", block)
    return text


# ── Helpers for md_to_telegram_html ──

_TABLE_ROW = re.compile(r"^\|(.+)\|$")
_TABLE_SEP = re.compile(r"^[\s|:-]+$")


def _stash_tables(text: str, put_fn, esc_fn) -> str:
    """Convert Markdown tables to key-value list format and stash them.

    | Name  | Age |
    |-------|-----|
    | Alice | 30  |   →   • Name: Alice, Age: 30
    | Bob   | 25  |       • Name: Bob, Age: 25
    """
    lines = text.split("\n")
    out: list[str] = []
    headers: list[str] = []
    data_rows: list[list[str]] = []

    def _flush():
        if not headers and not data_rows:
            return
        if headers and data_rows:
            items: list[str] = []
            for row in data_rows:
                pairs = ", ".join(
                    f"{headers[i]}: {row[i]}" if i < len(row) else headers[i]
                    for i in range(len(headers))
                )
                items.append(f"\u2022 {pairs}")
            out.append(put_fn(esc_fn("\n".join(items))))
        elif data_rows:
            # No header row — just bullet each row
            for row in data_rows:
                out.append(put_fn(esc_fn(f"\u2022 {', '.join(row)}")))
        headers.clear()
        data_rows.clear()

    for line in lines:
        m = _TABLE_ROW.match(line.strip())
        if m:
            if _TABLE_SEP.match(line.strip()):
                continue
            cells = [c.strip() for c in m.group(1).split("|")]
            if not headers:
                headers.extend(cells)
            else:
                data_rows.append(cells)
        else:
            _flush()
            out.append(line)
    _flush()
    return "\n".join(out)


_LIST_ITEM = re.compile(r"^( *)([-*+]|\d+\.)\s+(.*)$")
_BULLETS = ["\u2022", "\u25e6", "\u25aa"]  # •  ◦  ▪


def _convert_lists(text: str) -> str:
    """Convert Markdown list items to indented bullet / numbered lines."""
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        m = _LIST_ITEM.match(line)
        if m:
            depth = len(m.group(1)) // 2
            marker, content = m.group(2), m.group(3)
            px = "  " * depth
            if marker.rstrip(".").isdigit():
                out.append(f"{px}{marker} {content}")
            else:
                out.append(f"{px}{_BULLETS[min(depth, len(_BULLETS) - 1)]} {content}")
        else:
            out.append(line)
    return "\n".join(out)


def _convert_blockquotes(text: str) -> str:
    """Convert Markdown blockquotes (> text) to <blockquote> tags."""
    lines = text.split("\n")
    out: list[str] = []
    quote_buf: list[str] = []

    def _flush():
        if quote_buf:
            out.append("<blockquote>" + "\n".join(quote_buf) + "</blockquote>")
            quote_buf.clear()

    for line in lines:
        m = re.match(r"^&gt;\s?(.*)", line)  # > is already HTML-escaped at this point
        if m:
            quote_buf.append(m.group(1))
        else:
            _flush()
            out.append(line)
    _flush()
    return "\n".join(out)
