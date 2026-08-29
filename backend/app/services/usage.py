"""Per-user rate limiting + token usage tracking for cost control.

In-memory store by default so it runs with zero config. Swap the underlying
storage for Redis/Postgres (via the `database_url` setting) in production so
limits survive restarts and scale across instances.
"""
import time
from collections import defaultdict
from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class _UserState:
    requests: list[float] = field(default_factory=list)
    tokens_per_day: int = 0
    day_key: str = ""


class UsageTracker:
    def __init__(self) -> None:
        self._users: dict[str, _UserState] = defaultdict(_UserState)

    def check(self, user_id: str) -> tuple[bool, str]:
        """Return (ok, message). Enforces per-minute request cap."""
        state = self._users[user_id]
        now = time.time()

        # Drop requests older than the window
        state.requests = [t for t in state.requests if now - t < 60]
        if len(state.requests) >= settings.rate_limit_per_min:
            return False, "Rate limit exceeded. Slow down and try again shortly."
        return True, ""

    def consume(self, user_id: str, usage: dict | None = None) -> None:
        state = self._users[user_id]
        state.requests.append(time.time())

        # Daily token budget (per-user cost control)
        day = time.strftime("%Y-%m-%d")
        if state.day_key != day:
            state.day_key = day
            state.tokens_per_day = 0
        if usage:
            state.tokens_per_day += int(usage.get("total_tokens", 0))

    def remaining_tokens(self, user_id: str) -> int:
        state = self._users[user_id]
        return max(0, settings.rate_limit_tokens_per_day - state.tokens_per_day)


tracker = UsageTracker()