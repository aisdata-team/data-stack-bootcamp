import check_source_drift as drift
import pytest
from conftest import edit_front_matter

SHA_PIN = "0" * 40


@pytest.fixture
def fake(monkeypatch):
    """Map (repo, path, ref) → blob sha / None / FetchError. Anything unmapped is a test bug."""
    table = {}

    def fetch(repo, path, ref, token):
        value = table[(repo, path, ref)]
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(drift, "fetch_blob_sha", fetch)
    return table


def test_unchanged_is_clean(content, fake):
    fake[("warehouse", "README.md", SHA_PIN)] = "blob1"
    fake[("warehouse", "README.md", "main")] = "blob1"
    code, report = drift.run(content, "token")
    assert code == 0 and "All sources unchanged" in report


def test_changed_is_drift(content, fake):
    fake[("warehouse", "README.md", SHA_PIN)] = "blob1"
    fake[("warehouse", "README.md", "main")] = "blob2"
    code, report = drift.run(content, "token")
    assert code == 1 and "### changed" in report and "unit F1-01" in report


def test_missing_is_drift(content, fake):
    fake[("warehouse", "README.md", SHA_PIN)] = "blob1"
    fake[("warehouse", "README.md", "main")] = None
    code, report = drift.run(content, "token")
    assert code == 1 and "### missing" in report


def test_unreadable_source_is_not_clean(content, fake):
    fake[("warehouse", "README.md", SHA_PIN)] = drift.FetchError("HTTP 500")
    code, report = drift.run(content, "token")
    assert code == 2 and "not a clean result" in report


def test_wrong_pin_is_unreadable(content, fake):
    fake[("warehouse", "README.md", SHA_PIN)] = None
    code, report = drift.run(content, "token")
    assert code == 2 and "the pin is wrong" in report


def test_no_token_is_not_run(content, fake):
    code, report = drift.run(content, None)
    assert code == 2 and "NOT RUN" in report


def test_no_sources_is_not_run(content, fake):
    edit_front_matter(content / "units/F1-01-example/unit.md", lambda m: m.update(sources=[]))
    code, report = drift.run(content, "token")
    assert code == 2 and "NOT RUN" in report


def test_sources_are_deduplicated_and_every_citer_listed(content, fake):
    edit_front_matter(
        content / "units/F1-01-example/unit.md",
        lambda m: m["sources"].append(dict(m["sources"][0])),
    )
    cited = drift.collect_sources(content)
    assert cited == {("warehouse", "README.md", SHA_PIN): ["unit F1-01", "unit F1-01"]}
