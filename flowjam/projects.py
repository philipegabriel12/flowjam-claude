"""Parse #projects messages: a Drive folder link plus a 'X x Flowjam' title."""
import re
from dataclasses import dataclass

DRIVE_FOLDER = re.compile(r"https://drive\.google\.com/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]+)")
_TITLE = re.compile(r"(?:Flowjam\s+x\s+([^\n\-–|]+)|([^\n\-–|]+?)\s+x\s+Flowjam)", re.I)


@dataclass
class ProjectLink:
    message_id: str
    project: str
    folder_id: str
    url: str

    @property
    def target_folder(self) -> str:
        return f"Flowjam x {self.project}"


def parse_project_message(message_id: str, content: str) -> list[ProjectLink]:
    links = []
    title = _TITLE.search(DRIVE_FOLDER.sub("", content))
    project = (title[1] or title[2]).strip() if title else "Unknown"
    for m in DRIVE_FOLDER.finditer(content):
        links.append(ProjectLink(message_id, project, m[1], m[0]))
    return links
