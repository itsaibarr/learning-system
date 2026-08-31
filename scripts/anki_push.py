#!/usr/bin/env python3
"""Push approved card batches from anki/queue.md into Anki via AnkiConnect.

Usage: python3 scripts/anki_push.py [--dry-run]

Only batches with `status: approved` are pushed. A batch whose cards ALL get
added moves to anki/pushed.md; a batch with any rejected/duplicate card stays
in the queue so nothing is silently lost. Requires Anki running with the
AnkiConnect addon (localhost:8765).
"""

import argparse
import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ANKI_URL = "http://127.0.0.1:8765"
REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "anki" / "queue.md"
PUSHED = REPO / "anki" / "pushed.md"

BATCH_RE = re.compile(r"^## Batch:\s*(?P<name>[^|]+?)\s*\|\s*deck:\s*(?P<deck>[^|]+?)\s*\|\s*status:\s*(?P<status>\w+)\s*$")
FIELDS = {"A:": "back", "Tags:": "tags", "Src:": "src"}


def parse_queue(text):
    """Parse queue markdown into batches of cards, each batch carrying its
    [start, end) line span. Raises ValueError on malformed input."""
    lines = text.splitlines()
    batches = []
    card = None

    def close_card():
        nonlocal card
        if card is None:
            return
        if card["type"] == "basic" and not card.get("back"):
            raise ValueError(f"Basic card missing 'A:' line: {card.get('front', '?')!r}")
        if card["type"] == "cloze" and "{{c" not in card["text"]:
            raise ValueError(f"Cloze card has no {{{{cN::...}}}} deletion: {card['text']!r}")
        batches[-1]["cards"].append(card)
        card = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## Batch"):
            close_card()
            m = BATCH_RE.match(stripped)
            if not m:
                raise ValueError(f"Malformed batch header (need name | deck | status): {stripped!r}")
            if batches:
                batches[-1]["end"] = i
            batches.append({**m.groupdict(), "cards": [], "start": i, "end": len(lines)})
        elif stripped.startswith("Q:") or stripped.startswith("Text:"):
            close_card()
            if not batches:
                raise ValueError("Card found before any batch header")
            if stripped.startswith("Q:"):
                card = {"type": "basic", "front": stripped.removeprefix("Q:").strip(), "tags": [], "src": ""}
            else:
                card = {"type": "cloze", "text": stripped.removeprefix("Text:").strip(), "tags": [], "src": ""}
        elif card is not None:
            if not stripped:
                close_card()
            else:
                for prefix, key in FIELDS.items():
                    if stripped.startswith(prefix):
                        value = stripped.removeprefix(prefix).strip()
                        card[key] = value.split() if key == "tags" else value
                        break
                else:
                    raise ValueError(
                        f"Unrecognized line inside a card block (fields are single-line; "
                        f"end a card with a blank line): {stripped!r}")
    close_card()
    return batches


def to_anki_html(text):
    """Escape for Anki's HTML fields and convert $/$$ math to MathJax delimiters."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\$\$(.+?)\$\$", r"\\[\1\\]", text, flags=re.S)
    return re.sub(r"\$(.+?)\$", r"\\(\1\\)", text)


def build_notes(batch):
    """Turn a parsed batch into AnkiConnect addNotes payloads."""
    notes = []
    for card in batch["cards"]:
        src = f"Source: {to_anki_html(card['src'])}" if card["src"] else ""
        if card["type"] == "basic":
            back = to_anki_html(card["back"]) + (f"<br><br>{src}" if src else "")
            fields = {"Front": to_anki_html(card["front"]), "Back": back}
            model = "Basic"
        else:
            fields = {"Text": to_anki_html(card["text"]), "Back Extra": src}
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
    except OSError as e:
        raise RuntimeError(f"Cannot reach AnkiConnect at {ANKI_URL} — is Anki running with the AnkiConnect addon? ({e})")
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error on {action}: {result['error']}")
    return result["result"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="parse and report without pushing or rewriting")
    args = parser.parse_args()

    text = QUEUE.read_text()
    batches = parse_queue(text)
    approved = [b for b in batches if b["status"] == "approved"]
    if not approved:
        print("No approved batches in anki/queue.md — nothing to push.")
        return

    done, failure = [], None
    for batch in approved:
        if not batch["cards"]:
            failure = f"Batch {batch['name']!r} is approved but has no cards — fix the queue."
            break
        notes = build_notes(batch)
        print(f"Batch {batch['name']!r} → deck {batch['deck']!r}: {len(notes)} cards"
              + (" (dry run)" if args.dry_run else ""))
        if args.dry_run:
            continue
        try:
            anki("createDeck", deck=batch["deck"])
            ids = anki("addNotes", notes=notes)
        except RuntimeError as e:
            failure = str(e)
            break
        rejected = ids.count(None)
        if rejected:
            print(f"  {rejected} card(s) NOT added (duplicate or rejected by Anki) — "
                  f"batch stays in the queue; fix or remove those cards and re-push.")
        else:
            print(f"  added {len(ids)} cards")
            done.append(batch)

    # Move fully-pushed batches out of the queue by their parsed line spans.
    if done and not args.dry_run:
        lines = text.splitlines()
        moved_idx = {i for b in done for i in range(b["start"], b["end"])}
        moved = [lines[i] for i in sorted(moved_idx)]
        remaining = [l for i, l in enumerate(lines) if i not in moved_idx]
        with PUSHED.open("a") as f:
            f.write(f"\n<!-- pushed {date.today().isoformat()} -->\n" + "\n".join(moved) + "\n")
        QUEUE.write_text("\n".join(remaining).rstrip() + "\n")
        print(f"Moved {len(done)} batch(es) to anki/pushed.md.")

    if failure:
        raise SystemExit(f"Stopped: {failure}\nAlready-pushed batches were moved; the rest of the queue is untouched.")


if __name__ == "__main__":
    main()
