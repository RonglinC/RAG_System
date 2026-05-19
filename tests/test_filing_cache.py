from sec.filing_cache import FilingCache


def test_html_cache_roundtrip(tmp_path):
    cache = FilingCache(cache_dir=tmp_path / "cache", enabled=True)
    calls = {"n": 0}

    def fetch():
        calls["n"] += 1
        return "<html>filing</html>"

    a = cache.get_html("key1", fetch)
    b = cache.get_html("key1", fetch)
    assert a == b == "<html>filing</html>"
    assert calls["n"] == 1
