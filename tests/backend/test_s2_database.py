import pytest

@pytest.mark.xfail(strict=True, reason="Defect BE-001 / Baseline R-3: Sync SQLite blocks async loop")
def test_concurrent_write_locks():
    assert False
