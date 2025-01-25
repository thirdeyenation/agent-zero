# Agent Zero Project Documentation

This document provides a comprehensive overview of the Agent Zero project, including all actions taken, issues encountered, solutions implemented, and file management practices. It serves as a backup and reconfiguration guide.

## Project Overview

The Agent Zero project involves creating an autonomous AI agent framework capable of solving complex tasks using tools and subordinate agents. The project includes the development of core functionalities, AI/ML integration, UI design, and ensuring scalability and optimization.

## Core Principles

- Modularity: The framework is designed with modular components for easy maintenance and scalability.
- Role-Based Multi-Agent Cooperation: Agents are assigned specific roles and cooperate to achieve project goals.
- Advanced Orchestration: The framework implements advanced orchestration for efficient task delegation and management.
- Persistent Memory: The framework uses persistent memory to store previous solutions, code, facts, and instructions.
- Computer as a Tool: The operating system is used as a tool to accomplish tasks.
- Transparency: The framework maintains transparency and customizability.

## Implementation Details

### Tool Usage

The framework uses a variety of tools to accomplish tasks, including:

- `response`: Provides the final answer to the user.
- `call_subordinate`: Delegates subtasks to subordinate agents.
- `behaviour_adjustment`: Updates agent behavior per user request.
- `knowledge_tool`: Provides online and memory responses to specific questions.
- `memory_load`: Loads memories via query, threshold, limit, and filter.
- `memory_save`: Saves text to memory and returns an ID.
- `memory_delete`: Deletes memories by IDs.
- `memory_forget`: Removes memories by query, threshold, and filter.
- `code_execution_tool`: Executes terminal commands, python, and nodejs code.
- `input`: Provides keyboard input for terminal programs.
- `browser_agent`: Controls a playwright browser.

### Multi-Agent Cooperation

The framework uses a role-based multi-agent system, where agents communicate with each other, ask questions, give instructions, and provide guidance. Subordinate agents are created for specific tasks, such as AI/ML development, UI development, and content analysis.

### Workflow Management

The framework implements a flexible workflow management system that allows for both autonomous and semi-autonomous workflows. Human intervention is possible in complex workflows when needed.

### Memory Management

The framework uses persistent memory to store previous solutions, code, facts, and instructions. A mechanism is implemented for organizing and retrieving information from memory efficiently. The agent learns from its mistakes and improves its performance over time.

### Continuous Learning

The framework implements a mechanism for the agent to learn from its mistakes and improve its performance over time. Reflection prompts are used to encourage the agent to analyze its performance and identify areas for improvement.

### Communication

The framework emphasizes clear and effective communication between the agent and the user, as well as between agents. A multi-modal communication framework with progressive disclosure and psychological adaptation is used.

## Expected Improvements

- Enhanced executable actions.
- Chain of thought processing.
- Results-driven processes.

## Issues Encountered and Solutions

- **ValueError while parsing JSON response:** The agent encountered a ValueError while parsing a JSON response, specifically failing to convert a '+' character to a float. The agent attempted to inspect logs but the log file was not found. The agent then tried to explicitly set the 'reset' argument to "true" as a string.
- **Dependency conflict with typing-extensions:** The agent encountered a dependency conflict with typing-extensions during reinforcement learning setup. The agent tried upgrading and downgrading typing-extensions, but this caused further conflicts. The agent then tried to install a specific version of tf-agents, but this also failed. The agent created a virtual environment and attempted to install compatible versions of tf-agents and typing-extensions, but the reinforcement learning script was not found. The agent then tried to create the script directly, but encountered syntax errors. The agent then tried to install tensorflow, but this failed. The agent then tried to install tensorflow 2.12.0 and tf-agents 0.15.0 without dependencies, but this also failed. The agent is now in a loop, repeatedly trying to install tensorflow.
- **Installation issues with tensorflow and tf-agents:** The agent had issues installing tensorflow and tf-agents, which were resolved by skipping dependencies and upgrading tensorflow.
- **Issues with memory_load tool:** The memory_load tool did not work well with exact matches, requiring the use of IDs or more general queries.
- **Issues saving to memory using subordinate agent:** The agent had issues saving sentiment analysis accuracy scores to memory using the subordinate agent, so it saved them itself.

## File Management Practices

- The project directory is `the-agency-system/` with subdirectories for `curator-agent`, `manager-agent`, `shared`, `docs`, and `scripts`.
- Important files are saved in the `/root` directory, with documentation files in `/root/docs`, resource files in `/root/resources`, and scripts in `/root/scripts`.
- File names do not contain spaces.

## Important Files

- `/root/docs/agent_zero_documentation.md`: Documentation for the Agent Zero framework.
- `/root/docs/ui_wireframe.txt`: UI wireframe.
- `/root/scripts/reinforcement_learning.py`: Reinforcement learning script.
- `/root/output/sentiment_analysis_results.txt`: Sentiment analysis results.
- `/root/scripts/audio_analysis.py`: Audio analysis script.
- `/root/scripts/topic_extraction.py`: Topic extraction script.
- `/root/docs/self_improvement_tool_documentation.md`: Documentation for the self-improvement tool.
- `/root/agent_zero_project_documentation.md`: This documentation file.

## Memory IDs

- 8480d483-6442-4a39-8b79-906049f1b199
- 033f82af-aeb0-462d-a179-2bcc68eed563
- 3bbe98a6-8789-4a99-8138-5bae06f09e59
- ed5209c4-3636-4ad1-b2b1-572a2d48bc92
- dc05e288-8d30-46a4-a0e9-f2697dcf9ff0
- 529a07aa-dfdf-4833-85b3-4e030bf2854d
- 88d8f324-49e9-4994-8b79-6a2beef1ef91
- efc4ec64-ddb3-46a2-9bc3-5a307ddd41ab
- 0fff429b-baf5-401a-8de4-d453c20f1046
- 4a5883f8-2e0c-4466-84c0-cd1243cd4ea2
- 60572c85-5d7d-4adf-a3f5-4f353f169779
- 7bae213a-944e-4be2-8fc1-f2224b8b94fc
- dbb2d7d8-6750-4dd1-9626-1149c1b019e1
- 50b80616-c21a-44c0-a6df-c3853c1a6c9c
- 32c50eef-481d-4717-ad91-8897caede5bd