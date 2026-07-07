import pytest
@pytest.mark.xfail(strict=True, reason="Defect S1")
def test_rbac():
    assert False