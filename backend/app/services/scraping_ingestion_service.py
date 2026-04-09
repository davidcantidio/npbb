"""Service layer for internal scraping ingestion persistence."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

from sqlmodel import Session, select

logger = logging.getLogger("app.services.scraping_ingestion")

try:
    # TODO(npbb): confirmar nomes definitivos dos modelos ao integrar ORM de scraping.
    from app.models.scraping_models import (
        IndicatorsMonthly,
        IndicatorsSnapshot,
        PostCoauthor,
        PostHashtag,
        PostMention,
        ProfileSnapshot,
        ScrapingRun,
        SocialPost,
        Sponsor,
    )
except Exception:  # pragma: no cover - fallback para ambiente sem modelos plugados.
    IndicatorsMonthly = None
    IndicatorsSnapshot = None
    PostCoauthor = None
    PostHashtag = None
    PostMention = None
    ProfileSnapshot = None
    ScrapingRun = None
    SocialPost = None
    Sponsor = None

try:
    # TODO(npbb): confirmar contratos definitivos de schema ao integrar modulo.
    from app.schemas.scraping_ingestion import (
        ScrapingIngestionCountsOut,
        ScrapingIngestionPayload,
        ScrapingIngestionResponse,
    )
except Exception:  # pragma: no cover - fallback para valida apenas por tipagem dinamica.
    ScrapingIngestionCountsOut = dict[str, int]  # type: ignore[assignment]
    ScrapingIngestionPayload = Any  # type: ignore[assignment]
    ScrapingIngestionResponse = dict[str, Any]  # type: ignore[assignment]


class ScrapingIngestionServiceError(RuntimeError):
    """Erro de dominio padronizado para ingestao de scraping."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 500,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "status_code": self.status_code,
            "extra": self.extra,
        }


def ingest_scraping_payload(*, session: Session, payload: ScrapingIngestionPayload) -> ScrapingIngestionResponse:
    """Ingest payload validated by schema and persist with idempotent upserts."""

    payload_data = _payload_to_dict(payload)
    sponsor_slug = str(payload_data.get("sponsor_slug") or "").strip()
    sponsor_handle = _normalize_handle(
        payload_data.get("instagram_handle") or payload_data.get("handle") or payload_data.get("profile_handle")
    )

    if not sponsor_slug:
        raise ScrapingIngestionServiceError(
            code="SCRAPING_SPONSOR_SLUG_INVALID",
            message="Campo sponsor_slug e obrigatorio e nao pode ser vazio.",
            status_code=400,
        )
    if not _has_useful_payload_blocks(payload_data):
        raise ScrapingIngestionServiceError(
            code="SCRAPING_EMPTY_PAYLOAD",
            message="Payload sem blocos de posts, profiles ou indicators para ingestao.",
            status_code=400,
        )

    _ensure_scraping_models_configured()
    logger.info(
        "Iniciando ingestao de scraping.",
        extra={"sponsor_slug": sponsor_slug, "instagram_handle": sponsor_handle},
    )

    counts: dict[str, int] = {
        "posts_inserted": 0,
        "posts_updated": 0,
        "profiles_upserted": 0,
        "hashtags_inserted": 0,
        "mentions_inserted": 0,
        "coauthors_inserted": 0,
        "indicators_upserted": 0,
        "monthly_rows_upserted": 0,
    }

    try:
        sponsor = _upsert_sponsor(session=session, payload_data=payload_data)
        run = _create_scraping_run(session=session, sponsor=sponsor, payload_data=payload_data)

        posts_inserted, posts_updated, hashtags_inserted, mentions_inserted, coauthors_inserted = _upsert_social_posts(
            session=session,
            sponsor=sponsor,
            run=run,
            payload_data=payload_data,
        )
        counts["posts_inserted"] += posts_inserted
        counts["posts_updated"] += posts_updated
        counts["hashtags_inserted"] += hashtags_inserted
        counts["mentions_inserted"] += mentions_inserted
        counts["coauthors_inserted"] += coauthors_inserted

        counts["profiles_upserted"] += _upsert_profile_snapshots(
            session=session,
            sponsor=sponsor,
            run=run,
            payload_data=payload_data,
        )

        indicators_payload = payload_data.get("indicators")
        if isinstance(indicators_payload, dict):
            snapshot, indicators_upserted = _upsert_indicators_snapshot(
                session=session,
                sponsor=sponsor,
                run=run,
                indicators_payload=indicators_payload,
            )
            counts["indicators_upserted"] += indicators_upserted
            counts["monthly_rows_upserted"] += _upsert_indicators_monthly(
                session=session,
                sponsor=sponsor,
                snapshot=snapshot,
                indicators_payload=indicators_payload,
            )

        session.commit()
    except ScrapingIngestionServiceError as exc:
        session.rollback()
        logger.warning(
            "Falha de dominio na ingestao.",
            extra={
                "code": exc.code,
                "sponsor_slug": sponsor_slug,
                "instagram_handle": sponsor_handle,
            },
        )
        raise
    except Exception as exc:  # pragma: no cover - guardrail de erro inesperado.
        session.rollback()
        logger.exception(
            "Erro inesperado na ingestao de scraping.",
            extra={"sponsor_slug": sponsor_slug, "instagram_handle": sponsor_handle},
        )
        raise ScrapingIngestionServiceError(
            code="SCRAPING_INGESTION_INTERNAL_ERROR",
            message="Erro interno ao processar ingestao de scraping.",
            status_code=500,
            extra={"error_type": exc.__class__.__name__},
        ) from exc

    logger.info(
        "Ingestao de scraping finalizada.",
        extra={
            "sponsor_slug": sponsor_slug,
            "run_id": _entity_value(run, "id"),
            "counts": counts,
        },
    )
    return _build_response(
        sponsor=sponsor,
        run=run,
        counts=counts,
    )


def _upsert_sponsor(*, session: Session, payload_data: dict[str, Any]) -> Any:
    sponsor_slug = str(payload_data.get("sponsor_slug") or "").strip()
    instagram_handle = _normalize_handle(payload_data.get("instagram_handle") or payload_data.get("handle"))
    sponsor = None

    if sponsor_slug and _model_has_columns(Sponsor, "slug"):
        sponsor = _select_first(
            session=session,
            model=Sponsor,
            filters=[("slug", sponsor_slug)],
        )
    if sponsor is None and instagram_handle and _model_has_columns(Sponsor, "instagram_handle"):
        sponsor = _select_first(
            session=session,
            model=Sponsor,
            filters=[("instagram_handle", instagram_handle)],
        )

    mutable_fields = {
        "slug": sponsor_slug,
        "sponsor_slug": sponsor_slug,
        "name": payload_data.get("sponsor_name") or payload_data.get("name"),
        "instagram_handle": instagram_handle,
        "instagram_url": payload_data.get("instagram_url"),
        "status": payload_data.get("status"),
        "notes": payload_data.get("notes"),
    }
    if sponsor is None:
        sponsor = _build_entity(Sponsor, mutable_fields)
        session.add(sponsor)
        session.flush()
        return sponsor

    _apply_updates(entity=sponsor, values=mutable_fields, only_non_null=True)
    session.add(sponsor)
    session.flush()
    return sponsor


def _create_scraping_run(*, session: Session, sponsor: Any, payload_data: dict[str, Any]) -> Any:
    run_meta = payload_data.get("run_meta")
    if not isinstance(run_meta, dict):
        run_meta = {}
    meta_block = payload_data.get("meta")
    if isinstance(meta_block, dict):
        run_meta = {**run_meta, **meta_block}

    run_values = {
        "sponsor_id": _entity_value(sponsor, "id"),
        "run_meta": run_meta,
        "metadata_json": run_meta,
        "raw_json": run_meta,
        "run_handle": payload_data.get("run_handle") or run_meta.get("handle"),
        "started_at": _parse_iso_datetime(run_meta.get("runStartedAt") or run_meta.get("started_at")),
        "finished_at": _parse_iso_datetime(run_meta.get("runFinishedAt") or run_meta.get("finished_at")),
    }
    run = _build_entity(ScrapingRun, run_values)
    session.add(run)
    session.flush()
    return run


def _upsert_social_posts(
    *,
    session: Session,
    sponsor: Any,
    run: Any,
    payload_data: dict[str, Any],
) -> tuple[int, int, int, int, int]:
    posts_inserted = 0
    posts_updated = 0
    hashtags_inserted = 0
    mentions_inserted = 0
    coauthors_inserted = 0

    for platform, post in _iter_social_posts(payload_data):
        post_url = str(post.get("post_url") or post.get("postUrl") or post.get("url") or "").strip()
        shortcode = str(post.get("shortcode") or post.get("code") or "").strip()
        if post_url and not _is_valid_url(post_url):
            logger.warning(
                "Post ignorado por URL invalida.",
                extra={"platform": platform, "post_url": post_url},
            )
            continue
        if not post_url and not shortcode:
            logger.warning(
                "Post ignorado por chave natural ausente.",
                extra={"platform": platform},
            )
            continue

        existing_post = None
        if post_url and _model_has_columns(SocialPost, "platform", "post_url"):
            existing_post = _select_first(
                session=session,
                model=SocialPost,
                filters=[("platform", platform), ("post_url", post_url)],
            )
        if existing_post is None and platform == "instagram" and shortcode and _model_has_columns(
            SocialPost, "platform", "shortcode"
        ):
            existing_post = _select_first(
                session=session,
                model=SocialPost,
                filters=[("platform", platform), ("shortcode", shortcode)],
            )

        post_values = _build_post_values(
            sponsor=sponsor,
            run=run,
            platform=platform,
            post=post,
            post_url=post_url,
            shortcode=shortcode,
        )

        if existing_post is None:
            persisted_post = _build_entity(SocialPost, post_values)
            session.add(persisted_post)
            session.flush()
            posts_inserted += 1
        else:
            _apply_updates(entity=existing_post, values=post_values, only_non_null=True)
            session.add(existing_post)
            session.flush()
            persisted_post = existing_post
            posts_updated += 1

        hashtags_inserted += _replace_post_hashtags(session=session, post_entity=persisted_post, post_payload=post)
        mentions_inserted += _replace_post_mentions(session=session, post_entity=persisted_post, post_payload=post)
        coauthors_inserted += _replace_post_coauthors(session=session, post_entity=persisted_post, post_payload=post)

    return posts_inserted, posts_updated, hashtags_inserted, mentions_inserted, coauthors_inserted


def _replace_post_hashtags(*, session: Session, post_entity: Any, post_payload: dict[str, Any]) -> int:
    return _replace_post_children(
        session=session,
        child_model=PostHashtag,
        post_id=_entity_value(post_entity, "id"),
        value_field_candidates=("hashtag", "tag", "value"),
        values=_extract_values_from_post(
            post_payload,
            list_keys=("hashtags", "hashtags_list"),
            raw_keys=("hashtags_raw",),
        ),
    )


def _replace_post_mentions(*, session: Session, post_entity: Any, post_payload: dict[str, Any]) -> int:
    values = [_normalize_handle(value) for value in _extract_values_from_post(
        post_payload,
        list_keys=("mentions", "mentions_list"),
        raw_keys=("mentions_raw",),
    )]
    values = [value for value in values if value]
    return _replace_post_children(
        session=session,
        child_model=PostMention,
        post_id=_entity_value(post_entity, "id"),
        value_field_candidates=("mention_handle", "handle", "username", "value"),
        values=values,
    )


def _replace_post_coauthors(*, session: Session, post_entity: Any, post_payload: dict[str, Any]) -> int:
    values = [_normalize_handle(value) for value in _extract_values_from_post(
        post_payload,
        list_keys=("coauthors", "coauthors_list"),
        raw_keys=("coauthors_raw",),
    )]
    values = [value for value in values if value]
    return _replace_post_children(
        session=session,
        child_model=PostCoauthor,
        post_id=_entity_value(post_entity, "id"),
        value_field_candidates=("coauthor_handle", "handle", "username", "value"),
        values=values,
    )


def _upsert_profile_snapshots(*, session: Session, sponsor: Any, run: Any, payload_data: dict[str, Any]) -> int:
    upserts = 0
    sponsor_id = _entity_value(sponsor, "id")
    run_id = _entity_value(run, "id")
    for profile in _iter_profile_snapshots(payload_data):
        platform = str(profile.get("platform") or "").strip().lower()
        fetched_at = _parse_iso_datetime(profile.get("fetched_at") or profile.get("fetchedAt"))
        if not platform or fetched_at is None:
            continue

        existing = None
        if _model_has_columns(ProfileSnapshot, "sponsor_id", "platform", "fetched_at"):
            existing = _select_first(
                session=session,
                model=ProfileSnapshot,
                filters=[("sponsor_id", sponsor_id), ("platform", platform), ("fetched_at", fetched_at)],
            )

        values = {
            "run_id": run_id,
            "sponsor_id": sponsor_id,
            "platform": platform,
            "fetched_at": fetched_at,
            "profile_url": profile.get("profile_url") or profile.get("profileUrl"),
            "raw_json": profile,
            "followers": profile.get("followers"),
            "following": profile.get("following"),
            "posts_count": profile.get("posts_count") or profile.get("postsCount"),
            "engagement_rate": profile.get("engagement_rate") or profile.get("engagementRate"),
        }

        if existing is None:
            entity = _build_entity(ProfileSnapshot, values)
            session.add(entity)
        else:
            _apply_updates(entity=existing, values=values, only_non_null=True)
            session.add(existing)
        session.flush()
        upserts += 1
    return upserts


def _upsert_indicators_snapshot(*, session: Session, sponsor: Any, run: Any, indicators_payload: dict[str, Any]) -> tuple[Any, int]:
    run_id = _entity_value(run, "id")
    sponsor_id = _entity_value(sponsor, "id")
    snapshot = None
    if _model_has_columns(IndicatorsSnapshot, "run_id"):
        snapshot = _select_first(
            session=session,
            model=IndicatorsSnapshot,
            filters=[("run_id", run_id)],
        )

    values = {
        "run_id": run_id,
        "sponsor_id": sponsor_id,
        "indicators_json": indicators_payload.get("structured") or indicators_payload.get("json") or indicators_payload,
        "indicators_csv_flat": indicators_payload.get("flat") or indicators_payload.get("csv_flat"),
        "raw_json": indicators_payload,
        "generated_at_utc": _parse_iso_datetime(
            indicators_payload.get("generated_at") or indicators_payload.get("generatedAt")
        ),
    }

    if snapshot is None:
        snapshot = _build_entity(IndicatorsSnapshot, values)
        session.add(snapshot)
    else:
        _apply_updates(entity=snapshot, values=values, only_non_null=True)
        session.add(snapshot)
    session.flush()
    return snapshot, 1


def _upsert_indicators_monthly(
    *,
    session: Session,
    sponsor: Any,
    snapshot: Any,
    indicators_payload: dict[str, Any],
) -> int:
    monthly_rows = _extract_monthly_rows(indicators_payload)
    if not monthly_rows:
        return 0

    sponsor_id = _entity_value(sponsor, "id")
    snapshot_id = _entity_value(snapshot, "id")
    upserted = 0

    for row in monthly_rows:
        month = str(row.get("month") or "").strip()
        if not _is_valid_year_month(month):
            raise ScrapingIngestionServiceError(
                code="SCRAPING_MONTH_INVALID",
                message=f"Mes invalido em indicadores mensais: {month!r}.",
                status_code=400,
                extra={"month": month},
            )

        existing = None
        if _model_has_columns(IndicatorsMonthly, "snapshot_id", "month"):
            existing = _select_first(
                session=session,
                model=IndicatorsMonthly,
                filters=[("snapshot_id", snapshot_id), ("month", month)],
            )
        elif _model_has_columns(IndicatorsMonthly, "sponsor_id", "month"):
            existing = _select_first(
                session=session,
                model=IndicatorsMonthly,
                filters=[("sponsor_id", sponsor_id), ("month", month)],
            )

        values = {"snapshot_id": snapshot_id, "sponsor_id": sponsor_id, "month": month, "raw_json": row}
        for key, value in row.items():
            if key != "month":
                values[key] = value

        if existing is None:
            entity = _build_entity(IndicatorsMonthly, values)
            session.add(entity)
        else:
            _apply_updates(entity=existing, values=values, only_non_null=True)
            session.add(existing)
        session.flush()
        upserted += 1

    return upserted


def _normalize_handle(value: Any) -> str:
    handle = str(value or "").strip().lower()
    if not handle:
        return ""
    return handle[1:] if handle.startswith("@") else handle


def _parse_iso_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _split_pipe_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        merged: list[str] = []
        for item in value:
            merged.extend(_split_pipe_values(item))
        return merged
    text = str(value).strip()
    if not text:
        return []
    if "|" in text:
        chunks = text.split("|")
    else:
        chunks = [text]
    normalized = []
    seen = set()
    for chunk in chunks:
        item = str(chunk).strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized


def _ensure_scraping_models_configured() -> None:
    missing = [
        name
        for name, model in (
            ("Sponsor", Sponsor),
            ("ScrapingRun", ScrapingRun),
            ("SocialPost", SocialPost),
            ("PostHashtag", PostHashtag),
            ("PostMention", PostMention),
            ("PostCoauthor", PostCoauthor),
            ("ProfileSnapshot", ProfileSnapshot),
            ("IndicatorsSnapshot", IndicatorsSnapshot),
            ("IndicatorsMonthly", IndicatorsMonthly),
        )
        if model is None
    ]
    if missing:
        raise ScrapingIngestionServiceError(
            code="SCRAPING_MODELS_NOT_CONFIGURED",
            message="Modelos relacionais de scraping ainda nao estao configurados no backend.",
            status_code=500,
            extra={"missing_models": missing},
        )


def _payload_to_dict(payload: Any) -> dict[str, Any]:
    if hasattr(payload, "model_dump"):
        dumped = payload.model_dump(exclude_none=True)
        if isinstance(dumped, dict):
            return dumped
    if isinstance(payload, dict):
        return payload
    return {}


def _has_useful_payload_blocks(payload_data: dict[str, Any]) -> bool:
    has_posts = any(True for _ in _iter_social_posts(payload_data))
    has_profiles = any(True for _ in _iter_profile_snapshots(payload_data))
    has_indicators = isinstance(payload_data.get("indicators"), dict)
    return has_posts or has_profiles or has_indicators


def _iter_social_posts(payload_data: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    platforms = payload_data.get("platforms")
    if not isinstance(platforms, dict):
        platforms = {}

    candidates: Sequence[tuple[str, Any]] = (
        ("instagram", platforms.get("instagramPosts") or payload_data.get("instagram_posts")),
        ("x", platforms.get("xTweets") or payload_data.get("x_posts") or payload_data.get("tweets")),
        ("tiktok", platforms.get("tiktokVideos") or payload_data.get("tiktok_posts")),
    )
    for platform, maybe_rows in candidates:
        if isinstance(maybe_rows, list):
            for row in maybe_rows:
                if isinstance(row, dict):
                    yield platform, row


def _iter_profile_snapshots(payload_data: dict[str, Any]) -> Iterable[dict[str, Any]]:
    profiles = payload_data.get("profiles")
    if isinstance(profiles, dict):
        for platform, profile in profiles.items():
            if isinstance(profile, dict):
                row = dict(profile)
                row.setdefault("platform", str(platform).lower())
                yield row
    snapshot_list = payload_data.get("profile_snapshots")
    if isinstance(snapshot_list, list):
        for row in snapshot_list:
            if isinstance(row, dict):
                yield row


def _extract_monthly_rows(indicators_payload: dict[str, Any]) -> list[dict[str, Any]]:
    monthly = indicators_payload.get("monthly")
    if isinstance(monthly, list):
        return [row for row in monthly if isinstance(row, dict)]
    if isinstance(monthly, dict):
        rows: list[dict[str, Any]] = []
        for month, row in monthly.items():
            if isinstance(row, dict):
                materialized = dict(row)
            else:
                materialized = {"value": row}
            materialized.setdefault("month", month)
            rows.append(materialized)
        return rows
    return []


def _extract_values_from_post(
    post_payload: dict[str, Any],
    *,
    list_keys: Sequence[str],
    raw_keys: Sequence[str],
) -> list[str]:
    values: list[str] = []
    for key in list_keys:
        raw = post_payload.get(key)
        if isinstance(raw, list):
            for item in raw:
                if item is not None:
                    values.append(str(item))
    for key in raw_keys:
        values.extend(_split_pipe_values(post_payload.get(key)))

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = str(value).strip()
        if not item:
            continue
        dedupe_key = item.casefold()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(item)
    return normalized


def _replace_post_children(
    *,
    session: Session,
    child_model: Any,
    post_id: Any,
    value_field_candidates: Sequence[str],
    values: Sequence[str],
) -> int:
    if child_model is None or post_id is None:
        return 0
    post_field = _first_supported_column(child_model, ("post_id", "social_post_id"))
    value_field = _first_supported_column(child_model, value_field_candidates)
    if post_field is None or value_field is None:
        return 0

    existing_children = _select_all(
        session=session,
        model=child_model,
        filters=[(post_field, post_id)],
    )
    for child in existing_children:
        session.delete(child)
    session.flush()

    inserted = 0
    for value in values:
        data = {post_field: post_id, value_field: value}
        entity = _build_entity(child_model, data)
        session.add(entity)
        inserted += 1
    if inserted:
        session.flush()
    return inserted


def _build_post_values(*, sponsor: Any, run: Any, platform: str, post: dict[str, Any], post_url: str, shortcode: str) -> dict[str, Any]:
    values = {
        "run_id": _entity_value(run, "id"),
        "sponsor_id": _entity_value(sponsor, "id"),
        "platform": platform,
        "post_url": post_url or None,
        "shortcode": shortcode or None,
        "raw_json": post,
        "caption": post.get("caption") or post.get("text") or post.get("content"),
        "published_at": _parse_iso_datetime(post.get("published_at") or post.get("publishedAt")),
        "likes_count": post.get("likes_count") or post.get("likes"),
        "comments_count": post.get("comments_count") or post.get("comments"),
        "shares_count": post.get("shares_count") or post.get("shares"),
        "views_count": post.get("views_count") or post.get("views"),
        "engagement_rate": post.get("engagement_rate") or post.get("engagementRate"),
        "hashtags_raw": post.get("hashtags_raw") or "|".join(
            _extract_values_from_post(post, list_keys=("hashtags",), raw_keys=())
        ),
        "mentions_raw": post.get("mentions_raw") or "|".join(
            _extract_values_from_post(post, list_keys=("mentions",), raw_keys=())
        ),
        "coauthors_raw": post.get("coauthors_raw") or "|".join(
            _extract_values_from_post(post, list_keys=("coauthors",), raw_keys=())
        ),
    }
    return values


def _build_response(*, sponsor: Any, run: Any, counts: dict[str, int]) -> ScrapingIngestionResponse:
    response_data: dict[str, Any] = {
        "run_id": _entity_value(run, "id"),
        "ingestion_id": _entity_value(run, "id"),
        "sponsor_id": _entity_value(sponsor, "id"),
        "sponsor_slug": _entity_value(sponsor, "slug") or _entity_value(sponsor, "sponsor_slug"),
        "posts_inserted": counts["posts_inserted"],
        "posts_updated": counts["posts_updated"],
        "profiles_upserted": counts["profiles_upserted"],
        "hashtags_inserted": counts["hashtags_inserted"],
        "mentions_inserted": counts["mentions_inserted"],
        "coauthors_inserted": counts["coauthors_inserted"],
        "indicators_upserted": counts["indicators_upserted"],
        "monthly_rows_upserted": counts["monthly_rows_upserted"],
        # Compatibilidade retroativa com logs do router.
        "profiles_inserted": counts["profiles_upserted"],
        "profiles_updated": 0,
        "indicators_inserted": counts["indicators_upserted"],
        "indicators_updated": 0,
    }

    counts_type = ScrapingIngestionCountsOut
    if hasattr(counts_type, "__call__") and counts_type is not dict:
        try:
            response_data["counts"] = counts_type(
                posts_inserted=counts["posts_inserted"],
                posts_updated=counts["posts_updated"],
                profiles_upserted=counts["profiles_upserted"],
                hashtags_inserted=counts["hashtags_inserted"],
                mentions_inserted=counts["mentions_inserted"],
                coauthors_inserted=counts["coauthors_inserted"],
                indicators_upserted=counts["indicators_upserted"],
                monthly_rows_upserted=counts["monthly_rows_upserted"],
            )
        except Exception:
            response_data["counts"] = {
                "posts_inserted": counts["posts_inserted"],
                "posts_updated": counts["posts_updated"],
                "profiles_upserted": counts["profiles_upserted"],
                "hashtags_inserted": counts["hashtags_inserted"],
                "mentions_inserted": counts["mentions_inserted"],
                "coauthors_inserted": counts["coauthors_inserted"],
                "indicators_upserted": counts["indicators_upserted"],
                "monthly_rows_upserted": counts["monthly_rows_upserted"],
            }
    else:
        response_data["counts"] = {
            "posts_inserted": counts["posts_inserted"],
            "posts_updated": counts["posts_updated"],
            "profiles_upserted": counts["profiles_upserted"],
            "hashtags_inserted": counts["hashtags_inserted"],
            "mentions_inserted": counts["mentions_inserted"],
            "coauthors_inserted": counts["coauthors_inserted"],
            "indicators_upserted": counts["indicators_upserted"],
            "monthly_rows_upserted": counts["monthly_rows_upserted"],
        }

    response_type = ScrapingIngestionResponse
    if hasattr(response_type, "model_validate"):
        try:
            return response_type.model_validate(response_data)  # type: ignore[return-value]
        except Exception:
            return response_data  # type: ignore[return-value]
    if hasattr(response_type, "__call__") and response_type is not dict:
        try:
            return response_type(**response_data)  # type: ignore[return-value]
        except Exception:
            return response_data  # type: ignore[return-value]
    return response_data  # type: ignore[return-value]


def _select_first(*, session: Session, model: Any, filters: Sequence[tuple[str, Any]]) -> Any | None:
    if model is None:
        return None
    stmt = select(model)
    applied_filter = False
    for field, value in filters:
        if not _model_has_columns(model, field):
            continue
        stmt = stmt.where(getattr(model, field) == value)
        applied_filter = True
    if not applied_filter:
        return None
    return session.exec(stmt).first()


def _select_all(*, session: Session, model: Any, filters: Sequence[tuple[str, Any]]) -> list[Any]:
    if model is None:
        return []
    stmt = select(model)
    applied_filter = False
    for field, value in filters:
        if not _model_has_columns(model, field):
            continue
        stmt = stmt.where(getattr(model, field) == value)
        applied_filter = True
    if not applied_filter:
        return []
    return list(session.exec(stmt).all())


def _build_entity(model: Any, values: dict[str, Any]) -> Any:
    if model is None:
        raise ScrapingIngestionServiceError(
            code="SCRAPING_MODEL_UNAVAILABLE",
            message="Modelo relacional de scraping indisponivel.",
            status_code=500,
        )
    return model(**_filter_known_columns(model, values))


def _apply_updates(*, entity: Any, values: dict[str, Any], only_non_null: bool) -> None:
    columns = _model_columns(entity.__class__)
    for key, value in values.items():
        if key not in columns:
            continue
        if only_non_null and value is None:
            continue
        setattr(entity, key, value)


def _entity_value(entity: Any, field: str) -> Any:
    if entity is None:
        return None
    return getattr(entity, field, None)


def _filter_known_columns(model: Any, values: dict[str, Any]) -> dict[str, Any]:
    columns = _model_columns(model)
    return {key: value for key, value in values.items() if key in columns and value is not None}


def _model_has_columns(model: Any, *fields: str) -> bool:
    if model is None:
        return False
    columns = _model_columns(model)
    return all(field in columns for field in fields)


def _first_supported_column(model: Any, candidates: Sequence[str]) -> str | None:
    columns = _model_columns(model)
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _model_columns(model: Any) -> set[str]:
    fields = getattr(model, "__fields__", None)
    if isinstance(fields, dict):
        return set(fields.keys())
    annotations = getattr(model, "__annotations__", None)
    if isinstance(annotations, dict):
        return set(annotations.keys())
    return set()


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return bool(parsed.scheme and parsed.netloc)


def _is_valid_year_month(value: str) -> bool:
    if not re.match(r"^\d{4}-\d{2}$", value):
        return False
    _, month = value.split("-")
    month_number = int(month)
    return 1 <= month_number <= 12
