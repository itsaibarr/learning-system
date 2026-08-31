#!/usr/bin/env python3
"""Push approved card batches from anki/queue.md into Anki via AnkiConnect.

Usage: python3 scripts/anki_push.py [--dry-run]

Only batches with `status: approved` are pushed. Pushed batches move to
anki/pushed.md (date-stamped); draft batches stay in the queue untouched.
Requires Anki running with the AnkiConnect addon (localhost:8765).
"""

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ANKI_URL = "http://127.0.0.1:8765"
REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "anki" / "queue.md"
PUSHED = REPO / "anki" / "pushed.md"

BATCH_RE = re.compile(r"^## Batch:\s*(?P<name>[^|]+?)\s*\|\s*deck:\s*(?P<deck>[^|]+?)\s*\|\s*status:\s*(?P<status>\w+)\s*$")


def parse_queue(text):
    """Parse queue markdown into batches of cards. Raises ValueError on malformed input."""
    batches = []
    card = None

    def close_card():
        nonlocal card
        if card is None:
            return
        if card["type"] == "basic" and not card.get("back"):
            raise ValueError(f"Basic card missing 'A:' line: {card.get('front', '?')!r}")
        batches[-1]["cards"].append(card)
        card = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Batch"):
            close_card()
            m = BATCH_RE.match(stripped)
            if not m:
                raise ValueError(f"Malformed batch header (need name | deck | status): {stripped!r}")
            batches.append({**m.groupdict(), "cards": []})
        elif stripped.startswith("Q:"):
            close_card()
            if not batches:
                raise ValueError("Card found before any batch header")
            card = {"type": "basic", "front": stripped[2:].strip(), "tags": [], "src": ""}
        elif stripped.startswith("Text:"):
            close_card()
            if not batches:
                raise ValueError("Card found before any batch header")
            card = {"type": "cloze", "text": stripped[5:].strip(), "tags": [], "src": ""}
        elif card is not None and stripped.startswith("A:"):
            card["back"] = stripped[2:].strip()
        elif card is not None and stripped.startswith("Tags:"):
            card["tags"] = stripped[5:].split()
        elif card is not None and stripped.startswith("Src:"):
            card["src"] = stripped[4:].strip()
        elif not stripped:
            close_card()
    close_card()
    return batches


def build_notes(batch):
    """Turn a parsed batch into AnkiConnect addNotes payloads."""
    notes = []
    for card in batch["cards"]:
        src = f"<br><br>Source: {card['src']}" if card["src"] else ""
        if card["type"] == "basic":
            fields = {"Front": card["front"], "Back": card["back"] + src}
            model = "Basic"
        else:
            fields = {"Text": card["text"], "Back Extra": src.removeprefix("<br><br>")}
            model = "Cloze"
        notes.append({
            "deckName": batch["deck"],
            "modelName": model,
            "fields": fields,
            "tags": card["tags"],
            "options": {"allowDuplicate": False},
        })
    return notes


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(ANKI_URL, payload), timeout=10) as resp:
            result = json.load(resp)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Cannot reach AnkiConnect at {ANKI_URL} — is Anki running with the AnkiConnect addon? ({e})")
    if result.get("error"):
        sys.exit(f"AnkiConnect error on {action}: {result['error']}")
    return result["result"]


def main():
    dry_run = "--dry-run" in sys.argv
    batches = parse_queue(QUEUE.read_text())
    approved = [b for b in batches if b["status"] == "approved"]
    if not approved:
        print("No approved batches in anki/queue.md — nothing to push.")
        return

    for batch in approved:
        notes = build_notes(batch)
        print(f"Batch {batch['name']!r} → deck {batch['deck']!r}: {len(notes)} cards"
              + (" (dry run)" if dry_run else ""))
        if dry_run:
            continue
        anki("createDeck", deck=batch["deck"])
        ids = anki("addNotes", notes=notes)
        skipped = ids.count(None)
        print(f"  added {len(ids) - skipped}, skipped {skipped} duplicates")

    if dry_run:
        return

    # Move approved batches out of the queue into pushed.md.
    remaining, moved, current = [], [], None
    for line in QUEUE.read_text().splitlines():
        m = BATCH_RE.match(line.strip())
        if m:
            current = m.group("status")
        (moved if current == "approved" else remaining).append(line)
    stamp = f"\n<!-- pushed {date.today().isoformat()} -->\n"
    with PUSHED.open("a") as f:
        f.write(stamp + "\n".join(moved) + "\n")
    QUEUE.write_text("\n".join(remaining).rstrip() + "\n")
    print(f"Moved {len(approved)} batch(es) to anki/pushed.md.")


if __name__ == "__main__":
    main()
