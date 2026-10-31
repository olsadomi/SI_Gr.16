import pytest

from src.config import require_local_target


@pytest.mark.parametrize("url", ["http://localhost:8888", "http://127.0.0.1:8888", "http://host.docker.internal:8888"])
def test_local_targets_are_allowed(url):
    require_local_target(url)


def test_remote_target_is_refused():
    with pytest.raises(RuntimeError):
        require_local_target("https://example.com")

