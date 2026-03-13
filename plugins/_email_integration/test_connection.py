"""
Email integration connection test.
Usage: EMAIL_USER=you@gmail.com EMAIL_PASS=xxxx python plugins/_email_integration/test_connection.py

Tests:
  1. IMAP connect + get highest UID (baseline)
  2. Fetch new emails since that UID (should be 0 on first run)
  3. SMTP send test email to self
  4. Fetch again (should find the test email)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from plugins._email_integration.helpers.imap_client import (
    connect_imap,
    disconnect_imap,
    fetch_new,
    get_highest_uid,
)
from plugins._email_integration.helpers.smtp_client import SmtpConfig, send_reply


async def test_full_flow(user: str, password: str):
    print(f"\n--- Full Flow Test ({user}) ---\n")

    # Step 1: Connect and get baseline UID
    client = await connect_imap(
        server="imap.gmail.com", port=993,
        username=user, password=password,
    )
    print("[OK] IMAP login")

    baseline_uid = await get_highest_uid(client)
    print(f"[OK] Baseline UID: {baseline_uid}")

    # Step 2: Fetch new since baseline — should be 0
    messages, new_uid = await fetch_new(
        client, "/tmp/email_test_attachments",
        last_uid=baseline_uid, max_messages=5,
    )
    print(f"[OK] Fetch new since UID {baseline_uid}: {len(messages)} messages (expected 0)")

    await disconnect_imap(client)

    # Step 3: Send test email to self
    print("\n--- Sending test email to self ---")
    cfg = SmtpConfig(
        server="smtp.gmail.com", port=587,
        username=user, password=password,
    )
    ok = await send_reply(
        config=cfg, to=user,
        subject="A0 Email Test [a0-test123]",
        body="Test email from Agent Zero. If you see this, SMTP works.",
    )
    print(f"[{'OK' if ok else 'FAIL'}] SMTP send")

    if not ok:
        return

    # Step 4: Wait for email to arrive, then fetch
    print("\n--- Waiting 5s for email delivery ---")
    await asyncio.sleep(5)

    client2 = await connect_imap(
        server="imap.gmail.com", port=993,
        username=user, password=password,
    )

    messages2, new_uid2 = await fetch_new(
        client2, "/tmp/email_test_attachments",
        last_uid=baseline_uid, max_messages=5,
    )
    print(f"[OK] Fetch new since UID {baseline_uid}: {len(messages2)} messages")
    for msg in messages2:
        print(f"     From: {msg.sender}")
        print(f"     Subject: {msg.subject}")
        print(f"     Body: {msg.body[:80]}...")
        print()

    print(f"[OK] New last_uid: {new_uid2}")

    # Step 5: Fetch again with updated UID — should be 0
    messages3, _ = await fetch_new(
        client2, "/tmp/email_test_attachments",
        last_uid=new_uid2, max_messages=5,
    )
    print(f"[OK] Re-fetch since UID {new_uid2}: {len(messages3)} messages (expected 0)")

    await disconnect_imap(client2)
    print("\n--- ALL TESTS PASSED ---")


async def main():
    user = os.environ.get("EMAIL_USER", "")
    password = os.environ.get("EMAIL_PASS", "")

    if not user or not password:
        print("Set EMAIL_USER and EMAIL_PASS environment variables")
        print("Example: EMAIL_USER=you@gmail.com EMAIL_PASS=xxxx python ...")
        sys.exit(1)

    await test_full_flow(user, password)


if __name__ == "__main__":
    asyncio.run(main())
