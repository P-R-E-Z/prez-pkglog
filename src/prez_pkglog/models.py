from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Literal, TypedDict

Scope = Literal["user", "system"]


class PkgEventDict(TypedDict):
    name: str
    version: str
    manager: str
    scope: Scope
    when: str
    repository: str | None


@dataclass
class PkgEvent:
    name: str
    version: str
    manager: str
    scope: Scope
    repository: str | None = None
    when: datetime = datetime.now(timezone.utc)

    def to_dict(self) -> PkgEventDict:
        d = asdict(self)
        d["when"] = self.when.isoformat(timespec="seconds") + "Z"
        d["repository"] = self.repository
        return d  # type: ignore
