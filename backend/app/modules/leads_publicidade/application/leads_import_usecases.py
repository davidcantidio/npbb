"""Compatibility shim for app.modules.lead_imports.application.leads_import_usecases."""

from app.modules.leads_publicidade._compat import alias_module

alias_module(__name__, globals())
