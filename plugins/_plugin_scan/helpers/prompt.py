import json
from pathlib import Path

_DIR  = Path(__file__).parent.parent
_CFG  = json.loads((_DIR / "webui" / "plugin-scan-checks.json").read_text())
_TMPL = (_DIR / "webui" / "plugin-scan-prompt.md").read_text()


def build_prompt(git_url: str, checks: list | None = None) -> str:
    ratings, all_checks = _CFG["ratings"], _CFG["checks"]
    keys = [k for k in (checks or all_checks) if k in all_checks]

    subs = {
        "GIT_URL": git_url,
        "SELECTED_CHECKS": "\n".join(f"- **{all_checks[k]['label']}**" for k in keys),
        "CHECK_DETAILS": "\n\n".join(
            f"#### {c['label']}\n{c['detail']}\n\nCriteria:\n"
            + "\n".join(f"  - {ratings[l]['icon']} {d}" for l, d in c["criteria"].items())
            for c in (all_checks[k] for k in keys)
        ),
        "STATUS_LEGEND": "\n".join(f"- {r['icon']} **{r['label']}**" for r in ratings.values()),
        "RATING_ICONS":   "/".join(r["icon"] for r in ratings.values()),
        "RATING_PASS":    ratings["pass"]["icon"],
        "RATING_WARNING": ratings["warning"]["icon"],
        "RATING_FAIL":    ratings["fail"]["icon"],
    }
    prompt = _TMPL
    for key, val in subs.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", val)
    return prompt
