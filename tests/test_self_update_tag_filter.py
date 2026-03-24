import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.modules["giturlparse"] = types.SimpleNamespace(parse=lambda *args, **kwargs: None)

from helpers import self_update


def test_self_update_minimum_selector_tag_is_enforced():
    assert self_update.is_valid_selector_tag("v0.9.9")
    assert self_update._is_selector_supported_tag("v0.9.9.0")
    assert self_update._is_selector_supported_tag("v0.10.0.0")
    assert self_update.is_valid_selector_tag("v0.9.12.5-pre")
    assert not self_update.is_valid_selector_tag("0.9.9")
    assert not self_update.is_valid_selector_tag("v0.9")
    assert not self_update._is_selector_supported_tag("v0.9.8.9")
    assert not self_update._is_selector_supported_tag("v0.7.0.0")


def test_self_update_frontend_filters_old_tag_suggestions():
    store_path = (
        PROJECT_ROOT
        / "webui"
        / "components"
        / "settings"
        / "external"
        / "self-update-store.js"
    )
    content = store_path.read_text(encoding="utf-8")

    assert "const MIN_SELECTOR_VERSION = [0, 9, 9];" in content
    assert "response.tags.filter((tag) => this.isSupportedSuggestionTag(tag))" in content
    assert "if (!this.parseSelectorTag(this.form.tag)) {" in content
