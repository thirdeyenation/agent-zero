"""
Email dispatch logic — routes inbound emails to chats. 

No agent deps in pure helpers.
"""

import re
from dataclasses import dataclass
from typing import Literal

# Pattern for extracting chat thread ID from email subject
# Matches: [a0-xxxxxxxx] at end of subject
_THREAD_ID_RE = re.compile(r"\[a0-([a-zA-Z0-9]+)\]")

# Context data keys
CTX_EMAIL_HANDLER = "_email_handler"
CTX_EMAIL_SENDER = "_email_sender"
CTX_EMAIL_THREAD_ID = "_email_thread_id"
CTX_EMAIL_SUBJECT = "_email_subject"
CTX_EMAIL_MESSAGE_ID = "_email_message_id"
CTX_EMAIL_REFERENCES = "_email_references"
CTX_EMAIL_ATTACHMENTS = "_email_response_attachments"

DispatchAction = Literal["new_chat", "continue_chat", "intervene_soft", "intervene_hard"]


@dataclass
class DispatchDecision:
    action: DispatchAction
    context_id: str = ""
    reason: str = ""


def extract_thread_id(subject: str) -> str:
    match = _THREAD_ID_RE.search(subject)
    return match.group(1) if match else ""


def build_reply_subject(original_subject: str, thread_id: str) -> str:
    clean = _THREAD_ID_RE.sub("", original_subject).strip()
    if not clean.lower().startswith("re:"):
        clean = f"Re: {clean}"
    return f"{clean} [a0-{thread_id}]"


def build_chat_summary(context_id: str, data: dict) -> dict:
    return {
        "context_id": context_id,
        "thread_id": data.get(CTX_EMAIL_THREAD_ID, ""),
        "sender": data.get(CTX_EMAIL_SENDER, ""),
        "subject": data.get(CTX_EMAIL_SUBJECT, ""),
        "handler": data.get(CTX_EMAIL_HANDLER, ""),
    }


# ------------------------------------------------------------------
# Dispatcher prompt builders
# ------------------------------------------------------------------

def format_chats_list(existing_chats: list[dict]) -> str:
    if not existing_chats:
        return "No existing chats for this handler."
    lines = []
    for c in existing_chats[:20]:
        lines.append(
            f"- context_id={c['context_id']} thread_id={c.get('thread_id', '')} "
            f"sender={c.get('sender', '')} subject={c.get('subject', '')}"
        )
    return "\n".join(lines)


def parse_dispatcher_response(response: str) -> DispatchDecision:
    line = response.strip().split("\n")[0].strip()
    parts = line.split(None, 2)

    if len(parts) < 2:
        return DispatchDecision(action="new_chat", reason="unparseable response")

    action_raw = parts[0].upper()
    ctx_id = parts[1] if parts[1] != "_" else ""
    reason = parts[2] if len(parts) > 2 else ""

    action_map: dict[str, DispatchAction] = {
        "NEW_CHAT": "new_chat",
        "CONTINUE": "continue_chat",
        "INTERVENE_SOFT": "intervene_soft",
        "INTERVENE_HARD": "intervene_hard",
    }
    action = action_map.get(action_raw, "new_chat")
    return DispatchDecision(action=action, context_id=ctx_id, reason=reason)
