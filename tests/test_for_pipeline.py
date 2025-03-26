import pytest


@pytest.mark.anyio()
async def test_for_pipeline() -> None:
    """Тест для нормальной работы pipeline."""

    assert 2 + 2 == 4
