"""Daily run: `python -m flowjam`.

1. New screenshots in #clockify -> hours/project/date -> data/hours.csv (+ pay)
2. New Drive links in #projects -> data/drive_jobs.json (copied into the Drive by Claude)
Only messages posted after the first run are processed.
"""
import csv
import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from .discord import Discord
from .pay import fmt_duration, parse_duration, pay_for
from .projects import parse_project_message
from .vision import extract_entries

DATA = Path("data")
STATE = DATA / "state.json"
HOURS = DATA / "hours.csv"
JOBS = DATA / "drive_jobs.json"
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def main() -> None:
    load_dotenv()
    DATA.mkdir(exist_ok=True)
    state = load_json(STATE, {})
    discord = Discord(os.environ["DISCORD_BOT_TOKEN"])
    rate = Decimal(os.environ.get("HOURLY_RATE_USD", "25"))
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    claude = anthropic.Anthropic()

    # 1. clockify screenshots
    ch = os.environ["DISCORD_CLOCKIFY_CHANNEL_ID"]
    first_run = ch not in state
    msgs = discord.messages_after(ch, state.get(ch))
    rows = []
    if not first_run:
        for m in msgs:
            for a in m.get("attachments", []):
                if a.get("content_type") not in IMAGE_TYPES:
                    continue
                for e in extract_entries(claude, model, discord.download(a["url"]), a["content_type"]):
                    secs = parse_duration(e["duration"]) if e.get("duration") else 0
                    rows.append({
                        "date": e.get("date") or "", "project": e.get("project") or "",
                        "duration": fmt_duration(secs), "seconds": secs,
                        "pay_usd": str(pay_for(secs, rate)),
                        "posted_by": m["author"]["username"], "message_id": m["id"], "image": a["url"],
                    })
    if msgs:
        state[ch] = max(msgs, key=lambda m: int(m["id"]))["id"]
    if rows:
        new_file = not HOURS.exists()
        with HOURS.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            if new_file:
                w.writeheader()
            w.writerows(rows)

    # 2. project drive links
    ch = os.environ["DISCORD_PROJECTS_CHANNEL_ID"]
    first_run_p = ch not in state
    msgs = discord.messages_after(ch, state.get(ch))
    jobs = load_json(JOBS, [])
    if not first_run_p:
        for m in msgs:
            for link in parse_project_message(m["id"], m.get("content", "")):
                jobs.append({**link.__dict__, "target_folder": link.target_folder, "status": "pending"})
    if msgs:
        state[ch] = max(msgs, key=lambda m: int(m["id"]))["id"]
    JOBS.write_text(json.dumps(jobs, indent=2))
    STATE.write_text(json.dumps(state, indent=2))

    # summary
    if first_run or first_run_p:
        print("First run: marked the current position, only new posts will be processed from now on.")
    total = sum(r["seconds"] for r in rows)
    print(f"[{date.today()}] {len(rows)} new clockify entries, {fmt_duration(total)} = ${pay_for(total, rate)}")
    for r in rows:
        print(f"  {r['date']}  {r['project']:<25} {r['duration']}  ${r['pay_usd']}")
    pending = [j for j in jobs if j["status"] == "pending"]
    print(f"{len(pending)} Drive folders waiting to be copied:")
    for j in pending:
        print(f"  {j['target_folder']}  <- {j['url']}")


if __name__ == "__main__":
    main()
