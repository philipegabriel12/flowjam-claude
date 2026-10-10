# flowjam-claude

Daily tool for the Flowjam Dreamteam Discord server.

- **#clockify**: reads each new screenshot, pulls out project, date and hours, and appends them to `data/hours.csv` with pay at $25/h prorated to the second (4:30:00 = $112.50).
- **#projects**: picks up new Google Drive folder links and queues them in `data/drive_jobs.json`, to be copied into liveiraph@gmail.com's Drive as `Flowjam x <Project>/Collect` (project files) and `Flowjam x <Project>/Ready` (renders).

Only posts made after the first run are processed.

## Setup

1. Discord Developer Portal: New Application > Bot > copy the token, turn on **Message Content Intent**. Invite it to Flowjam Dreamteam with the `View Channels` + `Read Message History` permissions.
2. `cp .env.example .env` and fill it in.
3. `pip install -r requirements.txt`

## Daily run

```
python -m flowjam
```

Then the Drive step runs through Claude with the Google Drive connector (signed in as liveiraph@gmail.com): for each `pending` job in `data/drive_jobs.json`, copy the shared folder's files into
`<parent>/Flowjam x <Project>/Collect` and the renders into `.../Ready`, then mark the job `done`.
Parent folder: https://drive.google.com/drive/folders/1BfxW9OhA3k1Q8adorleMfm82g21OPwFt
