# Chat Branching

Create a new chat from any existing point in a conversation.

## What It Does

This plugin adds an API endpoint that clones an existing chat context, trims its log history up to a selected message, gives the new chat a `(branch)` suffix, persists it immediately, and refreshes connected tabs so the new branch appears in the UI.

## Main Behavior

- **Clone context**
  - Serializes the current chat context and deserializes it into a brand-new context with a new ID.
- **Trim history**
  - Keeps log entries only up to and including the selected `log_no`.
  - Includes a fallback for cases where reloaded logs use sequential array indexes.
- **Persist immediately**
  - Saves the newly created branched chat to temporary chat storage.
- **Refresh UI state**
  - Marks state dirty for all tabs after the branch is created.

## Entry Points

- **API**
  - `api/branch_chat.py` implements the branching operation.
- **Extensions**
  - `extensions/` contains integration glue for making the feature available in the app.

## Plugin Metadata

- **Name**: `_chat_branching`
- **Title**: `Chat Branching`
- **Description**: Branch a chat from any message, creating a new chat with history up to that point.
