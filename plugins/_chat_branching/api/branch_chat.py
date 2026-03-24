import json
from datetime import datetime

from helpers.api import ApiHandler, Input, Output, Request, Response
from helpers.persist_chat import (
    _serialize_context,
    _deserialize_context,
    save_tmp_chat,
)
from agent import AgentContext

# Log types that produce a history message (via hist_add_* in Agent)
_HIST_LOG_TYPES = {"user", "agent", "tool", "warning"}


def _count_history_msgs(logs, agent_no):
    """Count log items that produced history messages for a specific agent."""
    return sum(
        1 for item in logs
        if item["type"] in _HIST_LOG_TYPES and item.get("agentno", 0) == agent_no
    )


def _trim_history_json(history_json, keep_count):
    """Trim a serialized history JSON string to keep only the first
    *keep_count* un-summarized messages.  Summarized bulks/topics are
    always preserved (they represent older history before any cut point)."""
    if not history_json:
        return history_json
    hist = json.loads(history_json)

    # Flatten messages from topics + current, count and trim
    remaining = keep_count
    trimmed_topics = []

    for topic in hist.get("topics", []):
        if topic.get("summary"):
            # Summarized topic — keep whole, don't count
            trimmed_topics.append(topic)
            continue
        msgs = topic.get("messages", [])
        if remaining >= len(msgs):
            trimmed_topics.append(topic)
            remaining -= len(msgs)
        elif remaining > 0:
            topic["messages"] = msgs[:remaining]
            trimmed_topics.append(topic)
            remaining = 0
        # else: drop entirely

    hist["topics"] = trimmed_topics

    # Trim current topic
    current = hist.get("current", {})
    if not current.get("summary"):
        msgs = current.get("messages", [])
        if remaining < len(msgs):
            current["messages"] = msgs[:remaining]

    hist["counter"] = keep_count
    return json.dumps(hist, ensure_ascii=False)


class BranchChat(ApiHandler):
    """Create a new chat branched from an existing chat at a specific log message."""

    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")
        log_no = input.get("log_no")  # LogItem.no from frontend

        if not ctxid:
            return Response("Missing context id", 400)
        if log_no is None:
            return Response("Missing log_no", 400)

        context = AgentContext.get(ctxid)
        if not context:
            return Response("Context not found", 404)

        # Serialize the source context
        data = _serialize_context(context)

        # Remove id so _deserialize_context generates a new one
        del data["id"]

        # Trim log entries: keep only items up to and including log_no.
        src_logs = data["log"]["logs"]
        cut_idx = None
        for i, item in enumerate(src_logs):
            if item["no"] == log_no:
                cut_idx = i
                break

        if cut_idx is None:
            if 0 <= log_no < len(src_logs):
                cut_idx = log_no
            else:
                return Response("log_no not found in chat log", 400)

        kept_logs = src_logs[: cut_idx + 1]
        data["log"]["logs"] = kept_logs

        # Trim agent history to match the log cut point
        for ag in data.get("agents", []):
            msg_count = _count_history_msgs(kept_logs, ag["number"])
            ag["history"] = _trim_history_json(ag.get("history", ""), msg_count)

        # Give the branch a distinguishable name
        src_name = data.get("name") or "Chat"
        data["name"] = f"{src_name} (branch)"
        data["created_at"] = datetime.now().isoformat()

        # Deserialize into a brand-new context (new id, fresh agent config)
        new_context = _deserialize_context(data)

        # Persist immediately
        save_tmp_chat(new_context)

        # Notify all tabs
        from helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="plugins.chat_branching.BranchChat")

        return {
            "ok": True,
            "ctxid": new_context.id,
            "message": "Chat branched successfully.",
        }