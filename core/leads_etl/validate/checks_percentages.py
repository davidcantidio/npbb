"""Public percentage-check API for shared lead ETL validation."""

from ._contracts import Check
from ._percentage_bounds_impl import PercentBoundsCheck
from ._percentage_config import (
    PercentSumRuleConfig,
    PercentageCheckConfig,
    PercentageCheckConfigError,
    load_percentage_check_configs,
)
from ._percentage_sum_impl import PercentSumCheck


def build_percentage_checks(configs: tuple[PercentageCheckConfig, ...]) -> tuple[Check, ...]:
    """Build percentage checks (bounds + sum) from dataset configs."""

    checks: list[Check] = []
    for config in configs:
        checks.append(PercentBoundsCheck(config))
        for rule in config.sum_rules:
            checks.append(PercentSumCheck(config, rule))
    return tuple(checks)


__all__ = [
    "PercentBoundsCheck",
    "PercentSumCheck",
    "PercentSumRuleConfig",
    "PercentageCheckConfig",
    "PercentageCheckConfigError",
    "build_percentage_checks",
    "load_percentage_check_configs",
]

