from quotasignal.core import format_usage, parse_usage


def payload(primary_used=12, secondary_used=34):
    return {
        "rateLimits": {},
        "rateLimitsByLimitId": {
            "codex": {
                "planType": "plus",
                "primary": {
                    "usedPercent": primary_used,
                    "windowDurationMins": 300,
                    "resetsAt": 2_000_000_000,
                },
                "secondary": {
                    "usedPercent": secondary_used,
                    "windowDurationMins": 10_080,
                    "resetsAt": 2_000_100_000,
                },
            }
        },
    }


def test_parse_usage_selects_longest_window_as_weekly():
    usage = parse_usage(payload(), fetched_at=1_900_000_000)

    assert usage.weekly.name == "week"
    assert usage.weekly.used_percent == 34
    assert usage.weekly.remaining_percent == 66
    assert usage.session is not None
    assert usage.session.name == "5h"
    assert usage.session.remaining_percent == 88
    assert usage.plan == "plus"


def test_format_compact_emphasizes_weekly_remaining():
    usage = parse_usage(payload(4, 21), fetched_at=1_900_000_000)

    assert format_usage(usage, compact=True) == "Q 79%"


def test_legacy_snapshot_is_supported():
    value = payload()
    value["rateLimits"] = value.pop("rateLimitsByLimitId")["codex"]

    assert parse_usage(value).weekly.remaining_percent == 66
