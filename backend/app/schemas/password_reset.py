"""Schemas para recuperacao de senha."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    token: str | None = None
    expires_at: datetime | None = None
    reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class ResetPasswordResponse(BaseModel):
    message: str
