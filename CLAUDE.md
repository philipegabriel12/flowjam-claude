# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install: `pip install -r requirements.txt` (tests also need `pytest`)
- Daily run: `python -m flowjam` (reads `.env`, see `.env.example`)
- Tests: `python -m pytest -q tests`; single test: `python -m pytest -q tests/test_parsing.py::test_pay_prorated_to_second`

## How it fits together

`flowjam/__main__.py` is the whole pipeline, run once a day by the owner only:

1. **#clockify** (`discord.py` → `vision.py` → `pay.py`): new image attachments are sent to Claude, which returns `{project, date, duration}` per time entry; each becomes a row in `data/hours.csv` with pay = seconds × rate / 3600 (default $25/h, prorated to the second, rounded to cents).
2. **#projects** (`projects.py`): Drive folder links plus the "X x Flowjam" / "Flowjam x X" title in the same message become `pending` jobs in `data/drive_jobs.json`.
3. **Drive copy is not done in Python** (the owner chose not to set up a Google Cloud project). When asked to run the daily job, Claude does it with the Google Drive connector, signed in as liveiraph@gmail.com: for each pending job, create `Flowjam x <Project>/Collect` (project files) and `Flowjam x <Project>/Ready` (renders) under parent folder `1BfxW9OhA3k1Q8adorleMfm82g21OPwFt`, copy the files, set the job's `status` to `done`.

`data/state.json` stores the last processed Discord message id per channel. The first run for a channel only records the latest id and processes nothing: the owner wants new posts only, never history.

`data/` and `.env` are gitignored; `data/hours.csv` is the payment ledger, so append to it, never rewrite it.
