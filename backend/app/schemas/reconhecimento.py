"""Schemas do reconhecimento de leads."""

from __future__ import annotations

from pydantic import BaseModel


class LeadRecognitionRead(BaseModel):
    lead_reconhecido: bool
    lead_id: int | None = None
