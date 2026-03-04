"""Public DQ report renderer API for shared lead ETL validation."""

from ._report_renderers import render_dq_report, render_dq_report_json

__all__ = ["render_dq_report", "render_dq_report_json"]

