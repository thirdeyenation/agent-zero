import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.modules["giturlparse"] = types.SimpleNamespace(parse=lambda *args, **kwargs: None)

from helpers import self_update


def test_self_update_selector_tags_use_two_segments_and_v1_floor():
    assert self_update.is_valid_selector_tag("v1.0")
    assert self_update.is_valid_selector_tag("v12.34")
    assert self_update.is_valid_selector_tag("v0.9")
    assert self_update._is_selector_supported_tag("v1.0")
    assert self_update._is_selector_supported_tag("v2.3")
    assert not self_update.is_valid_selector_tag("1.0")
    assert not self_update.is_valid_selector_tag("v1")
    assert not self_update.is_valid_selector_tag("v1.0.0")
    assert not self_update.is_valid_selector_tag("v1.0.0.1")
    assert not self_update._is_selector_supported_tag("v0.9")
    assert not self_update._is_selector_supported_tag("v0.99")


def test_self_update_selector_tags_are_sorted_numerically():
    assert self_update._sort_selector_supported_tags(["v1.9", "v2.0", "v1.10"]) == [
        "v2.0",
        "v1.10",
        "v1.9",
    ]


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

    assert "const MIN_SELECTOR_VERSION = [1, 0];" in content
    assert "response.tags.filter((tag) => this.isSupportedSuggestionTag(tag))" in content
    assert "Release tag must use the format vX.Y." in content
    assert "Release tag must be v1.0 or newer." in content
