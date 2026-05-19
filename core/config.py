"""Project-wide configuration and runtime mode flags.

EXPERIMENTAL_MODE controls whether prescriptive ("GPS") output is emitted.
Default ON until validation passes (single-user testing only).
COMMUNITY_RELEASE must be explicitly enabled to expose to public.
"""

from __future__ import annotations

import os


ALGORITHM_VERSION = "mvp-0.1.0"
ZIWEI_SCHOOL = "bac_phai"
ZIWEI_RULESET_ID = "bac_phai_v1"
ZIWEI_RULESET_LABEL = "Bắc phái (chuẩn vận hành hiện tại)"


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# ---------------------------------------------------------------------------
# Runtime mode flags
# ---------------------------------------------------------------------------

# Single-user experimental mode. While ON:
# - GPS / actionable-insight outputs include EXPERIMENTAL banner
# - Pre-registered prediction logging is enforced
# - Community-facing endpoints refuse prescriptive output
EXPERIMENTAL_MODE = _bool_env("YI_EXPERIMENTAL_MODE", True)

# Hard gate for community release. Requires explicit env override.
# Even if False, read-only chiêm tinh / lịch endpoints remain available;
# only the prescriptive GPS layer is hidden.
COMMUNITY_RELEASE = _bool_env("YI_COMMUNITY_RELEASE", False)

# Profile lock — single-user mode restricts GPS to one profile_hash only.
# Set via env: YI_LOCKED_PROFILE_HASH=<sha256-hex>
LOCKED_PROFILE_HASH = os.environ.get("YI_LOCKED_PROFILE_HASH", "").strip() or None


def gps_enabled_for(profile_hash: str | None) -> bool:
    """Return True if prescriptive GPS output is allowed for the given profile.

    Rules:
    - If COMMUNITY_RELEASE=True and EXPERIMENTAL_MODE=False → enabled for all.
    - If EXPERIMENTAL_MODE=True and LOCKED_PROFILE_HASH set → only that hash.
    - If EXPERIMENTAL_MODE=True and no LOCKED_PROFILE_HASH → enabled (single-user
      assumed; banner shown).
    - Otherwise disabled.
    """
    if COMMUNITY_RELEASE and not EXPERIMENTAL_MODE:
        return True
    if EXPERIMENTAL_MODE:
        if LOCKED_PROFILE_HASH is None:
            return True
        return profile_hash == LOCKED_PROFILE_HASH
    return False


def runtime_mode_banner() -> dict[str, object]:
    """Banner string included in GPS responses for transparency."""
    if EXPERIMENTAL_MODE:
        return {
            "mode": "EXPERIMENTAL",
            "message": (
                "Đầu ra GPS đang ở chế độ thử nghiệm cá nhân (single-user). "
                "Mọi prediction được lưu pre-registered, không sửa được sau khi xảy ra. "
                "Không phải lời tiên tri công khai."
            ),
            "community_release": COMMUNITY_RELEASE,
            "profile_locked": LOCKED_PROFILE_HASH is not None,
        }
    return {
        "mode": "PRODUCTION",
        "message": "Output đã qua giai đoạn validation.",
        "community_release": COMMUNITY_RELEASE,
        "profile_locked": LOCKED_PROFILE_HASH is not None,
    }
