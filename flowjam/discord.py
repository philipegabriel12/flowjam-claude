"""Minimal Discord REST client: read new messages from a channel."""
import httpx

API = "https://discord.com/api/v10"


class Discord:
    def __init__(self, token: str):
        self.http = httpx.Client(headers={"Authorization": f"Bot {token}"}, timeout=30)

    def messages_after(self, channel_id: str, after: str | None) -> list[dict]:
        """All messages newer than `after`, oldest first. With no `after`, returns []
        and the caller just records the latest id (we only process going forward)."""
        if after is None:
            r = self.http.get(f"{API}/channels/{channel_id}/messages", params={"limit": 1})
            r.raise_for_status()
            return r.json()
        out = []
        while True:
            r = self.http.get(f"{API}/channels/{channel_id}/messages", params={"after": after, "limit": 100})
            r.raise_for_status()
            batch = sorted(r.json(), key=lambda m: int(m["id"]))
            if not batch:
                return out
            out += batch
            after = batch[-1]["id"]

    def download(self, url: str) -> bytes:
        r = httpx.get(url, timeout=60)
        r.raise_for_status()
        return r.content
