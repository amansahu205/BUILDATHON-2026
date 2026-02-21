from .config import settings
from .services.case_store import CaseStore

_case_store: CaseStore | None = None


def get_case_store() -> CaseStore:
    global _case_store
    if _case_store is None:
        _case_store = CaseStore(settings.cases_file)
    return _case_store
