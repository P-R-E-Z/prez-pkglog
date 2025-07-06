from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

Scope = Literal["user", "system"]


class PkgEventDict(TypedDict):
    name: str
    version: str
    summary: str
    scope: Scope
    when: str
    location: str


@dataclass
class PkgEvent:
    name: str
    version: str
    summary: str
    scope: Scope
    location: Path
    when: datetime = datetime.utcnow()

    def to_dict(self) -> PkgEventDict:
        d = asdict(self)
        d["when"] = self.when.isoformat(timespec="seconds") + "Z"
        d["location"] = str(self.location)
        return d
