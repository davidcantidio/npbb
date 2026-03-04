"""Compatibility re-export for shared lead ETL DQ report renderers."""

from core.leads_etl.validate.render_dq_report import render_dq_report, render_dq_report_json

__all__ = ["render_dq_report", "render_dq_report_json"]
