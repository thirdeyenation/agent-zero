"""Core compaction logic for the compaction plugin."""
import asyncio
from typing import Callable

from agent import Agent
from helpers import history, tokens
from helpers.history import History, output_text
from helpers.log import Log
from helpers.persist_chat import save_tmp_chat, remove_msg_files
from helpers.state_monitor_integration import mark_dirty_all
from plugins._model_config.helpers.model_config import get_chat_model_config



async def run_compaction(context, use_chat_model: bool = True) -> None:
    """
    Compact the chat history into a single summarized message.
    
    This function:
    1. Extracts the full conversation text
    2. Estimates token count and checks against model context window
    3. If needed, splits history and summarizes iteratively
    4. Calls the LLM to generate a comprehensive summary
    5. Replaces the history with a single AI message containing the summary
    6. Resets the log and creates a response log item
    7. Persists the changes
    
    The function streams progress to the frontend via the log system.
    If any error occurs, the original history is preserved.
    """
    agent = context.agent0
    
    try:
        # Step 1: Extract full conversation text
        history_output = agent.history.output()
        full_text = output_text(history_output, ai_label="assistant", human_label="user")
        
        if not full_text.strip():
            raise ValueError("No conversation content to compact")
        
        # Step 2: Estimate tokens and get model config
        token_count = tokens.approximate_tokens(full_text)
        
        model_config = get_chat_model_config() if use_chat_model else None
        if model_config is None:
            # Fallback: use default context length
            ctx_length = 128000
        else:
            ctx_length = int(model_config.get("ctx_length", 128000))
        
        # Leave some buffer for the prompt and response
        max_input_tokens = int(ctx_length * 0.7)
        
        # Step 3: Create progress log item
        log_item = context.log.log(
            type="info",
            heading="Compacting chat history...",
            content=f"Analyzing {len(agent.history.current.messages)} messages (~{token_count} tokens)...",
        )
        
        # Step 4: Handle large histories by chunking if necessary
        if token_count > max_input_tokens:
            summary = await _compact_large_history(
                agent, full_text, token_count, max_input_tokens, log_item, use_chat_model
            )
        else:
            # Single-pass compaction
            summary = await _compact_single_pass(
                agent, full_text, log_item, use_chat_model
            )
        
        if not summary or not summary.strip():
            raise ValueError("Compaction produced empty summary")
        
        # Step 5: Replace history with compacted version
        agent.history = History(agent=agent)
        agent.history.add_message(
            ai=True,
            content=f"# Chat Compacted\n\n{summary}"
        )
        
        # Clear subordinate chain
        agent.data.pop(Agent.DATA_NAME_SUBORDINATE, None)
        context.streaming_agent = None
        
        # Step 6: Reset log and create response
        context.log.reset()
        context.log.log(
            type="response",
            heading="Chat Compacted",
            content=summary,
            update_progress="none",
        )
        
        # Step 7: Persist and notify
        save_tmp_chat(context)
        remove_msg_files(context.id)
        
        # Step 8: Force progress bar to inactive state LAST
        # This must happen after all log operations and persist
        context.log.set_progress("Waiting for input", 0, False)
        mark_dirty_all(reason="plugins.compaction.compact_chat")
        
    except Exception as e:
        # Log error but don't modify history
        context.log.log(
            type="error",
            heading="Compaction Failed",
            content=str(e),
        )
        mark_dirty_all(reason="plugins.compaction.compact_chat_error")
        raise


async def _compact_single_pass(
    agent, 
    full_text: str, 
    log_item,
    use_chat_model: bool
) -> str:
    """Compact history in a single LLM call."""
    
    system_prompt = agent.read_prompt("compact.sys.md")
    user_prompt = agent.read_prompt("compact.msg.md", conversation=full_text)
    
    if use_chat_model:
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        async def chat_stream_cb(chunk: str, total: str):
            if chunk:
                log_item.stream(content=chunk)
        
        summary, _ = await agent.call_chat_model(
            messages=messages,
            response_callback=chat_stream_cb,
        )
    else:
        async def util_stream_cb(chunk: str):
            if chunk:
                log_item.stream(content=chunk)
        
        summary = await agent.call_utility_model(
            system=system_prompt,
            message=user_prompt,
            callback=util_stream_cb,
        )
    
    return summary


async def _compact_large_history(
    agent,
    full_text: str,
    token_count: int,
    max_input_tokens: int,
    log_item,
    use_chat_model: bool
) -> str:
    """
    Handle large histories by splitting into chunks and summarizing iteratively.
    """
    log_item.update(
        content=f"History is large (~{token_count} tokens). Splitting into chunks...",
    )
    
    # Split conversation into roughly equal halves
    lines = full_text.split('\n')
    mid = len(lines) // 2
    
    chunks = [
        '\n'.join(lines[:mid]),
        '\n'.join(lines[mid:])
    ]
    
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        log_item.update(
            content=f"Summarizing part {i}/{len(chunks)}...",
        )
        
        system_prompt = agent.read_prompt("compact.sys.md")
        user_prompt = agent.read_prompt("compact.msg.md", conversation=chunk)
        
        if use_chat_model:
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            chunk_summary, _ = await agent.call_chat_model(
                messages=messages,
                response_callback=None,  # No streaming for chunks
            )
        else:
            chunk_summary = await agent.call_utility_model(
                system=system_prompt,
                message=user_prompt,
                callback=None,
            )
        
        summaries.append(chunk_summary)
    
    # Combine summaries
    combined = "\n\n---\n\n".join(summaries)
    
    log_item.update(
        content="Creating final summary from parts...",
    )
    
    # Final compaction of combined summaries
    final_prompt = agent.read_prompt("compact.sys.md")
    final_user = agent.read_prompt(
        "compact.msg.md", 
        conversation=f"This is a multi-part conversation. Here are summaries of each part:\n\n{combined}"
    )
    
    if use_chat_model:
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=final_prompt),
            HumanMessage(content=final_user)
        ]
        final_summary, _ = await agent.call_chat_model(
            messages=messages,
            response_callback=lambda chunk, total: log_item.stream(content=chunk),
        )
    else:
        final_summary = await agent.call_utility_model(
            system=final_prompt,
            message=final_user,
            callback=lambda chunk: log_item.stream(content=chunk),
        )
    
    return final_summary
async def get_compaction_stats(context) -> dict:
    """
    Get statistics about the current chat for the confirmation modal.
    
    Returns:
        dict with message_count, token_count, model_name
    """
    agent = context.agent0
    
    # Count user-visible conversation turns only
    # 'user' = user sent a message, 'response' = agent final response
    # Other types (agent, tool, code_exe, etc.) are intermediate processing steps
    visible_types = {"user", "response"}
    message_count = sum(
        1 for item in context.log.logs
        if item.type in visible_types
    )
    
    # Estimate tokens
    history_output = agent.history.output()
    full_text = output_text(history_output, ai_label="assistant", human_label="user")
    token_count = tokens.approximate_tokens(full_text) if full_text else 0
    
    # Get model name
    model_config = get_chat_model_config()
    model_name = model_config.get("name", "Default Model") if model_config else "Utility Model"
    
    return {
        "message_count": message_count,
        "token_count": token_count,
        "model_name": model_name,
    }
