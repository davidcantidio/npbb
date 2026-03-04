"""Compatibility re-export for shared lead ETL access-control checks."""

from core.leads_etl.validate.checks_access_control import (
    AccessControlReconciliationCheck,
    AccessControlRuleFinding,
)

__all__ = ["AccessControlReconciliationCheck", "AccessControlRuleFinding"]
