import pytest

@pytest.mark.xfail(strict=True, reason="Defect ARCH-001 / Baseline R-4: Missing DGX Fallback")
def test_dgx_fallback_degradation():
    assert False
