import pytest

@pytest.mark.xfail(strict=True, reason="Defect A11Y-001: Keyboard traps in modal")
def test_modal_keyboard_navigation():
    assert False
