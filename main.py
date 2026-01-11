#!/usr/bin/env python3
"""
Instagram Agent Skills - Main Entry Point

A collection of 5 AI-powered agents for streamlining Instagram business communication.
"""

import os
from datetime import datetime
from agents import (
    AgentOrchestrator,
    TranslatorAgent,
    QuickResponseAgent,
    SentimentAgent,
    LeadQualifierAgent,
    MemoryAgent,
)
from business_config import BUSINESS_INFO, get_pricing_text, get_faq_text

# Try to import pyperclip for clipboard support
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


def copy_to_clipboard(text):
    """Copy text to clipboard if available."""
    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(text)
            return True
        except:
            return False
    return False


def log_conversation(client_id, message, reply, sentiment, lead_score):
    """Save conversation to log file."""
    log_dir = "logs"
    log_file = os.path.join(log_dir, "conversations.log")

    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
{'='*60}
[{timestamp}] Client: {client_id}
Sentiment: {sentiment} | Lead Score: {lead_score}
------------------------------------------------------------
CUSTOMER: {message}
BOT: {reply}
{'='*60}
"""

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)


def demo():
    """Demonstrate the agent skills with auto-reply."""
    print("=" * 60)
    print("amilie - Instagram Auto Reply Demo")
    print("=" * 60)

    # Initialize orchestrator (loads all agents)
    orchestrator = AgentOrchestrator()

    # Example incoming messages
    test_messages = [
        {
            "id": "msg_001",
            "client_id": "user_123",
            "content": "How much for a logo?",
        },
        {
            "id": "msg_002",
            "client_id": "user_456",
            "content": "What's the delivery time for a VTuber model?",
        },
        {
            "id": "msg_003",
            "client_id": "user_789",
            "content": "Do you offer revisions?",
        },
    ]

    print("\n[INBOX] Processing messages with AUTO-REPLY...\n")

    for msg in test_messages:
        print(f"From: {msg['client_id']}")
        print(f"Message: {msg['content']}")

        # Get automatic reply
        result = orchestrator.auto_reply(
            message=msg["content"],
            client_id=msg["client_id"],
        )

        print(f"\n[ANALYSIS] Language: {result['detected_language']} | Sentiment: {result['sentiment']} | Lead: {result['lead_score']}")
        print(f"\n[AUTO-REPLY] {result['auto_reply']}")

        # Log the conversation
        log_conversation(
            msg['client_id'],
            msg['content'],
            result['auto_reply'],
            result['sentiment'],
            result['lead_score']
        )

        print("-" * 60)

    print("\nDemo complete! Check logs/conversations.log for history.")
    print("=" * 60)


def auto_reply_mode():
    """Auto-reply mode - generates automatic responses."""
    orchestrator = AgentOrchestrator()

    print("\n" + "=" * 60)
    print("amilie - Instagram Auto Reply Bot")
    print("=" * 60)

    # Show pricing info
    print("\n" + get_pricing_text())
    print(get_faq_text())

    if CLIPBOARD_AVAILABLE:
        print("[OK] Auto-copy to clipboard ENABLED")
    else:
        print("[!] Install pyperclip for auto-copy: pip install pyperclip")

    print("\nCommands: 'new' = new client | 'logs' = view logs | 'quit' = exit")
    print("-" * 60)

    client_id = input("\nClient ID (or Enter for 'customer'): ").strip() or "customer"

    while True:
        print(f"\n[{client_id}]")
        message = input("Customer message: ").strip()

        if message.lower() == "quit":
            print("\nGoodbye! Check logs/conversations.log for history.")
            break

        if message.lower() == "new":
            client_id = input("New client ID: ").strip() or "customer"
            continue

        if message.lower() == "logs":
            print("\n--- Recent Conversations ---")
            try:
                with open("logs/conversations.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Show last 30 lines
                    print("".join(lines[-30:]))
            except FileNotFoundError:
                print("No logs yet.")
            continue

        if not message:
            continue

        # Generate automatic reply
        result = orchestrator.auto_reply(
            message=message,
            client_id=client_id,
        )

        print(f"\n[ANALYSIS]")
        print(f"  Language: {result['detected_language']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Priority: {result['priority']}/10")
        print(f"  Lead Score: {result['lead_score']}")

        reply = result['auto_reply']

        print(f"\n[AUTO-REPLY]")
        print(f"  {reply}")

        # Auto-copy to clipboard
        if copy_to_clipboard(reply):
            print("\n[COPIED] Reply copied to clipboard! Just Ctrl+V to paste.")
        else:
            print("\n[INFO] Copy the reply above manually.")

        # Log the conversation
        log_conversation(
            client_id,
            message,
            reply,
            result['sentiment'],
            result['lead_score']
        )

        print("-" * 60)


def interactive():
    """Interactive mode with suggestions (legacy)."""
    orchestrator = AgentOrchestrator()

    print("\n[BOT] Instagram Agent Skills - Interactive Mode")
    print("Type 'quit' to exit\n")

    client_id = input("Enter client ID (or press Enter for 'test_client'): ").strip()
    if not client_id:
        client_id = "test_client"

    while True:
        message = input(f"\n[{client_id}] Enter message: ").strip()

        if message.lower() == "quit":
            print("Goodbye!")
            break

        if not message:
            continue

        result = orchestrator.process_message(message, client_id)

        print(f"\n[ANALYSIS]")
        print(f"  Language: {result['detected_language']}")
        print(f"  Sentiment: {result['sentiment'].get('sentiment')} (Priority: {result['sentiment'].get('priority')}/10)")
        print(f"  Lead Score: {result['lead_qualification'].get('score')}")
        print(f"  Action: {result['recommended_action']}")

        print(f"\n[RESPONSES]")
        for i, suggestion in enumerate(result['suggested_responses'], 1):
            print(f"  {i}. {suggestion}")

        # Option to prepare a response
        choice = input("\nSelect response (1-3) or type custom, or press Enter to skip: ").strip()

        if choice in ["1", "2", "3"]:
            idx = int(choice) - 1
            if idx < len(result['suggested_responses']):
                response = result['suggested_responses'][idx]
                prepared = orchestrator.prepare_response(response, client_id)
                print(f"\n[SEND] Ready to send: {prepared['ready_to_send']}")
        elif choice:
            prepared = orchestrator.prepare_response(choice, client_id)
            print(f"\n[SEND] Ready to send: {prepared['ready_to_send']}")


if __name__ == "__main__":
    import sys

    print("\namilie - Instagram Agent Skills")
    print("================================")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            auto_reply_mode()
        elif sys.argv[1] == "--interactive":
            interactive()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python main.py           Run demo")
            print("  python main.py --auto    Auto-reply mode (recommended)")
            print("  python main.py --interactive  Manual selection mode")
        else:
            demo()
    else:
        demo()
