import pytest

@pytest.mark.xfail(strict=True, reason="Defect FE-001 / Baseline R-1: Hardcoded IPs")
def test_no_hardcoded_ips_in_bundle():
    assert False
