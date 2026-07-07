import pytest

@pytest.mark.xfail(strict=True, reason="Defect SEC-001 / Baseline R-9: Role-string auth bypass")
def test_reject_raw_role_string():
    assert False
