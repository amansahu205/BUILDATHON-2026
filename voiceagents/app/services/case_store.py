import json
import re
from pathlib import Path

from ..models import VerdictCase, CaseCreate, CaseUpdate


class CaseStore:
    """Thread-safe JSON-backed case storage."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cases: dict[str, VerdictCase] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._cases = {}
            return
        raw = json.loads(self._path.read_text())
        for item in raw:
            c = VerdictCase(**item)
            self._cases[c.id] = c

    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [c.model_dump() for c in self._cases.values()]
        self._path.write_text(json.dumps(payload, indent=2))

    def list_all(self) -> list[VerdictCase]:
        return list(self._cases.values())

    def get(self, case_id: str) -> VerdictCase | None:
        return self._cases.get(case_id)

    def create(self, data: CaseCreate) -> VerdictCase:
        cid = data.id or self._slugify(data.case_name)
        if cid in self._cases:
            raise ValueError(f"Case '{cid}' already exists")
        case = VerdictCase(id=cid, **data.model_dump(exclude={"id"}))
        self._cases[cid] = case
        self._flush()
        return case

    def update(self, case_id: str, data: CaseUpdate) -> VerdictCase | None:
        existing = self._cases.get(case_id)
        if not existing:
            return None
        updates = data.model_dump(exclude_none=True)
        merged = existing.model_dump()
        merged.update(updates)
        updated = VerdictCase(**merged)
        self._cases[case_id] = updated
        self._flush()
        return updated

    def delete(self, case_id: str) -> bool:
        if case_id not in self._cases:
            return False
        del self._cases[case_id]
        self._flush()
        return True

    @staticmethod
    def _slugify(name: str) -> str:
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "_", slug)
        return slug.strip("_")
