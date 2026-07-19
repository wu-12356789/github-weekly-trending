import httpx
import pytest
from src.github_client import GitHubClient


def test_client_does_not_retry_404(tmp_path):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(404, request=request)

    client = GitHubClient("", tmp_path)
    client.client.close()
    client.client = httpx.Client(base_url="https://api.github.com", transport=httpx.MockTransport(handler))
    with pytest.raises(RuntimeError, match="不可重试状态 404"):
        client.get("/repos/example/missing/releases/latest")
    client.close()
    assert calls == 1
