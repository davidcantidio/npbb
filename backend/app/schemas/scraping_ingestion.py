"""Schemas Pydantic para ingestao de dados do pipeline de scraping de redes sociais."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Sub-schemas: execution block
# ---------------------------------------------------------------------------


class ScrapingExecutionBlock(BaseModel):
    model_config = ConfigDict(extra="allow")

    handle: str | None = None
    athleteName: str | None = None
    since: str | None = None
    until: str | None = None
    max: int | None = None
    started_at: str | None = None
    finished_at: str | None = None


# ---------------------------------------------------------------------------
# Sub-schemas: platforms block
# ---------------------------------------------------------------------------


class ScrapingProfileSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    url: str | None = None
    fetched_at: str | None = None
    metaDescription: str | None = None
    ogTitle: str | None = None
    ogDescription: str | None = None
    followers: int | None = None
    following: int | None = None
    posts: int | None = None


class ScrapingInstagramPlatform(BaseModel):
    model_config = ConfigDict(extra="allow")

    posts: list[dict[str, Any]] = Field(default_factory=list)
    profile: ScrapingProfileSnapshot | None = None


class ScrapingXPlatform(BaseModel):
    model_config = ConfigDict(extra="allow")

    posts: list[dict[str, Any]] = Field(default_factory=list)
    profile: ScrapingProfileSnapshot | None = None


class ScrapingTikTokPlatform(BaseModel):
    model_config = ConfigDict(extra="allow")

    posts: list[dict[str, Any]] = Field(default_factory=list)
    profile: ScrapingProfileSnapshot | None = None


class ScrapingPlatformsBlock(BaseModel):
    model_config = ConfigDict(extra="allow")

    instagram: ScrapingInstagramPlatform | None = None
    x: ScrapingXPlatform | None = None
    tiktok: ScrapingTikTokPlatform | None = None


# ---------------------------------------------------------------------------
# Sub-schemas: summary block
# ---------------------------------------------------------------------------


class ScrapingSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_itens_ig: int | None = None
    total_itens_x: int | None = None
    total_itens_tiktok: int | None = None
    bb_mentions_ig: int | None = None
    bb_mentions_x: int | None = None
    bb_mentions_tiktok: int | None = None


# ---------------------------------------------------------------------------
# Sub-schemas: operational log line
# ---------------------------------------------------------------------------


class OperationalLogLine(BaseModel):
    model_config = ConfigDict(extra="allow")

    timestamp: str | None = None
    level: str | None = None
    message: str | None = None


# ---------------------------------------------------------------------------
# Main payload schema
# ---------------------------------------------------------------------------


class ScrapingIngestionPayload(BaseModel):
    """Payload enviado pelo scraper TypeScript ao endpoint de ingestao NPBB.

    O scraper envia um bloco ``execution`` com o handle do atleta/patrocinador e
    um bloco ``platforms`` com posts e profiles aninhados. O ``model_dump`` desta
    classe normaliza a estrutura para o formato esperado pelo service layer.
    """

    model_config = ConfigDict(extra="allow")

    # Bloco principal do scraper TypeScript
    execution: ScrapingExecutionBlock | None = None
    platforms: ScrapingPlatformsBlock | None = None
    summary: ScrapingSummary | None = None
    logs: list[OperationalLogLine] | None = None

    # Campos diretos (compatibilidade com payloads legados ou testes)
    sponsor_slug: str | None = None
    handle: str | None = None
    profile_handle: str | None = None
    instagram_handle: str | None = None
    sponsor_name: str | None = None

    @model_validator(mode="after")
    def _normalize_from_execution(self) -> "ScrapingIngestionPayload":
        """Preenche campos de identificacao a partir do bloco execution quando ausentes."""
        if self.execution:
            if not self.handle and self.execution.handle:
                self.handle = self.execution.handle
            if not self.instagram_handle and self.execution.handle:
                self.instagram_handle = self.execution.handle
            if not self.sponsor_slug and self.execution.handle:
                self.sponsor_slug = self.execution.handle
            if not self.sponsor_name and self.execution.athleteName:
                self.sponsor_name = self.execution.athleteName
        return self

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        """Serializa e normaliza a estrutura aninhada do scraper para o formato flat
        que o service layer utiliza."""
        data: dict[str, Any] = super().model_dump(**kwargs)

        # Extrair posts e profiles dos blocos aninhados para o formato flat
        ig = self.platforms.instagram if self.platforms else None
        x_block = self.platforms.x if self.platforms else None
        tiktok = self.platforms.tiktok if self.platforms else None

        platforms_flat: dict[str, Any] = data.get("platforms") or {}
        # Chaves esperadas pelo service (camelCase para compatibilidade com _iter_social_posts)
        platforms_flat["instagramPosts"] = (ig.posts if ig else []) or []
        platforms_flat["xTweets"] = (x_block.posts if x_block else []) or []
        platforms_flat["tiktokVideos"] = (tiktok.posts if tiktok else []) or []
        data["platforms"] = platforms_flat

        # Normalizar profiles no formato esperado pelo service (_iter_profile_snapshots)
        profiles: dict[str, Any] = {}
        if ig and ig.profile:
            profiles["instagram"] = ig.profile.model_dump(exclude_none=True) if hasattr(ig.profile, "model_dump") else {}
        if x_block and x_block.profile:
            profiles["x"] = x_block.profile.model_dump(exclude_none=True) if hasattr(x_block.profile, "model_dump") else {}
        if tiktok and tiktok.profile:
            profiles["tiktok"] = tiktok.profile.model_dump(exclude_none=True) if hasattr(tiktok.profile, "model_dump") else {}
        if profiles:
            data["profiles"] = profiles

        # Garantir que campos de identificacao estejam no nivel raiz
        if self.handle:
            data["handle"] = self.handle
        if self.instagram_handle:
            data["instagram_handle"] = self.instagram_handle
        if self.sponsor_slug:
            data["sponsor_slug"] = self.sponsor_slug
        if self.sponsor_name:
            data["sponsor_name"] = self.sponsor_name

        # Expor bloco run_meta para o service criar ScrapingRun
        if self.execution:
            exec_data = self.execution.model_dump(exclude_none=True) if hasattr(self.execution, "model_dump") else {}
            data.setdefault("run_meta", exec_data)
            data.setdefault("run_handle", self.execution.handle)

        return data


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ScrapingIngestionCountsOut(BaseModel):
    model_config = ConfigDict(extra="allow")

    posts_inserted: int = 0
    posts_updated: int = 0
    profiles_upserted: int = 0
    hashtags_inserted: int = 0
    mentions_inserted: int = 0
    coauthors_inserted: int = 0
    indicators_upserted: int = 0
    monthly_rows_upserted: int = 0


class ScrapingIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    ingestion_id: Any = None
    run_id: Any = None
    sponsor_id: Any = None
    sponsor_slug: str | None = None
    posts_inserted: int = 0
    posts_updated: int = 0
    profiles_inserted: int = 0
    profiles_updated: int = 0
    indicators_inserted: int = 0
    indicators_updated: int = 0
    profiles_upserted: int = 0
    hashtags_inserted: int = 0
    mentions_inserted: int = 0
    coauthors_inserted: int = 0
    indicators_upserted: int = 0
    monthly_rows_upserted: int = 0
    counts: ScrapingIngestionCountsOut | dict[str, int] | None = None
