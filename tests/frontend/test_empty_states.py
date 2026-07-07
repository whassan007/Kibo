import pytest

@pytest.mark.xfail(strict=True, reason="Defect FE-002 / Baseline R-4: Missing empty states")
def test_jurisdiction_dropdown_empty():
    assert False
