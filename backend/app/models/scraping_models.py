from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Index, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class SocialPlatform(str, Enum):
    INSTAGRAM = "instagram"
    X = "x"
    TIKTOK = "tiktok"


class RunStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNKNOWN = "unknown"


class BbConnectionType(str, Enum):
    MENTION = "mention"
    HASHTAG = "hashtag"
    MENTION_HASHTAG = "mention-hashtag"


class ScrapingSponsor(SQLModel, table=True):
    __tablename__ = "scraping_sponsors"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_scraping_sponsors_slug"),
        UniqueConstraint("instagram_handle", name="uq_scraping_sponsors_instagram_handle"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, max_length=160)
    name: Optional[str] = Field(default=None, max_length=240)
    instagram_handle: Optional[str] = Field(default=None, index=True, max_length=160)
    instagram_url: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    source_row_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False),
    )

    runs: List["ScrapingRun"] = Relationship(back_populates="sponsor")
    posts: List["SocialPost"] = Relationship(back_populates="sponsor")
    profiles: List["SocialProfileSnapshot"] = Relationship(back_populates="sponsor")
    indicator_snapshots: List["IndicatorsSnapshot"] = Relationship(back_populates="sponsor")


class ScrapingRun(SQLModel, table=True):
    __tablename__ = "scraping_runs"
    __table_args__ = (
        Index("ix_scraping_runs_sponsor_started_at", "sponsor_id", "started_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    sponsor_id: int = Field(foreign_key="scraping_sponsors.id", index=True)
    run_handle: str = Field(max_length=200)
    out_dir: Optional[str] = Field(default=None, max_length=1000)
    started_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    finished_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    since_date: Optional[date] = Field(default=None)
    until_date: Optional[date] = Field(default=None)
    max_items: Optional[int] = Field(default=None)
    scrape_instagram: bool = Field(default=False)
    scrape_x: bool = Field(default=False)
    scrape_tiktok: bool = Field(default=False)
    run_status: RunStatus = Field(
        default=RunStatus.UNKNOWN,
        sa_column=Column(
            SQLEnum(RunStatus, name="scraping_run_status", values_callable=_enum_values),
            nullable=False,
            index=True,
        ),
    )
    source_files_hash: Optional[str] = Field(default=None, max_length=128)
    run_csv_path: Optional[str] = Field(default=None, max_length=1000)
    run_log_path: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )

    sponsor: Optional["ScrapingSponsor"] = Relationship(back_populates="runs")
    posts: List["SocialPost"] = Relationship(back_populates="run")
    profiles: List["SocialProfileSnapshot"] = Relationship(back_populates="run")
    indicator_snapshot: Optional["IndicatorsSnapshot"] = Relationship(back_populates="run")


class SocialPost(SQLModel, table=True):
    __tablename__ = "scraping_social_posts"
    __table_args__ = (
        UniqueConstraint("platform", "post_url", name="uq_scraping_social_posts_platform_post_url"),
        Index(
            "ix_scraping_social_posts_sponsor_platform_post_datetime",
            "sponsor_id",
            "platform",
            "post_datetime",
        ),
        Index(
            "ix_scraping_social_posts_sponsor_is_bb_mention",
            "sponsor_id",
            "is_bb_mention",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="scraping_runs.id", index=True)
    sponsor_id: int = Field(foreign_key="scraping_sponsors.id", index=True)
    platform: SocialPlatform = Field(
        sa_column=Column(
            SQLEnum(SocialPlatform, name="scraping_social_platform", values_callable=_enum_values),
            nullable=False,
            index=True,
        ),
    )
    post_url: str = Field(max_length=2000)
    shortcode: Optional[str] = Field(default=None, index=True, max_length=120)
    post_datetime: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    post_date: Optional[date] = Field(default=None)
    text_content: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    hashtags_raw: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    mentions_raw: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    owner_username: Optional[str] = Field(default=None, index=True, max_length=160)
    is_owner_profile: bool = Field(default=False)
    media_type: Optional[str] = Field(default=None, max_length=80)
    is_collab: bool = Field(default=False)
    coauthors_raw: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    paid_partnership: bool = Field(default=False)
    paid_partner: Optional[str] = Field(default=None, max_length=240)
    location: Optional[str] = Field(default=None, max_length=400)
    likes: Optional[int] = Field(default=None)
    comments: Optional[int] = Field(default=None)
    views: Optional[int] = Field(default=None)
    plays_or_views: Optional[int] = Field(default=None)
    replies: Optional[int] = Field(default=None)
    reposts: Optional[int] = Field(default=None)
    shares: Optional[int] = Field(default=None)
    is_bb_mention: bool = Field(default=False, index=True)
    bb_connection_type: Optional[BbConnectionType] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(BbConnectionType, name="scraping_bb_connection_type", values_callable=_enum_values),
            nullable=True,
        ),
    )
    bb_markers_count: int = Field(default=0)
    scraped_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    raw_row_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False),
    )

    run: Optional["ScrapingRun"] = Relationship(back_populates="posts")
    sponsor: Optional["ScrapingSponsor"] = Relationship(back_populates="posts")
    hashtags: List["PostHashtag"] = Relationship(back_populates="post")
    mentions: List["PostMention"] = Relationship(back_populates="post")
    coauthors: List["PostCoauthor"] = Relationship(back_populates="post")


class PostHashtag(SQLModel, table=True):
    __tablename__ = "scraping_post_hashtags"

    post_id: int = Field(foreign_key="scraping_social_posts.id", primary_key=True)
    hashtag: str = Field(primary_key=True, max_length=160)

    post: Optional["SocialPost"] = Relationship(back_populates="hashtags")


class PostMention(SQLModel, table=True):
    __tablename__ = "scraping_post_mentions"

    post_id: int = Field(foreign_key="scraping_social_posts.id", primary_key=True)
    mention_handle: str = Field(primary_key=True, max_length=160)

    post: Optional["SocialPost"] = Relationship(back_populates="mentions")


class PostCoauthor(SQLModel, table=True):
    __tablename__ = "scraping_post_coauthors"

    post_id: int = Field(foreign_key="scraping_social_posts.id", primary_key=True)
    coauthor_handle: str = Field(primary_key=True, max_length=160)

    post: Optional["SocialPost"] = Relationship(back_populates="coauthors")


class SocialProfileSnapshot(SQLModel, table=True):
    __tablename__ = "scraping_profile_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "platform",
            "profile_url",
            "fetched_at",
            name="uq_scraping_profile_snapshots_platform_url_fetched",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="scraping_runs.id", index=True)
    sponsor_id: int = Field(foreign_key="scraping_sponsors.id", index=True)
    platform: SocialPlatform = Field(
        sa_column=Column(
            SQLEnum(SocialPlatform, name="scraping_social_platform", values_callable=_enum_values),
            nullable=False,
            index=True,
        ),
    )
    profile_url: str = Field(max_length=2000)
    fetched_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    username: Optional[str] = Field(default=None, max_length=160)
    display_name: Optional[str] = Field(default=None, max_length=240)
    followers: Optional[int] = Field(default=None)
    following: Optional[int] = Field(default=None)
    posts_count: Optional[int] = Field(default=None)
    likes_total: Optional[int] = Field(default=None)
    bio: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    external_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    meta_description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    og_title: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    og_description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    raw_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )

    run: Optional["ScrapingRun"] = Relationship(back_populates="profiles")
    sponsor: Optional["ScrapingSponsor"] = Relationship(back_populates="profiles")


class IndicatorsSnapshot(SQLModel, table=True):
    __tablename__ = "scraping_indicators_snapshot"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="scraping_runs.id", unique=True, index=True)
    sponsor_id: int = Field(foreign_key="scraping_sponsors.id", index=True)
    handler: str = Field(max_length=200)
    generated_at_utc: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    source_indicadores_csv_path: Optional[str] = Field(default=None, max_length=1000)
    source_indicadores_json_path: Optional[str] = Field(default=None, max_length=1000)
    indicators_csv_flat_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    indicators_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )

    run: Optional["ScrapingRun"] = Relationship(back_populates="indicator_snapshot")
    sponsor: Optional["ScrapingSponsor"] = Relationship(back_populates="indicator_snapshots")
    monthly: List["IndicatorsMonthly"] = Relationship(back_populates="snapshot")


class IndicatorsMonthly(SQLModel, table=True):
    __tablename__ = "scraping_indicators_monthly"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "month", name="uq_scraping_indicators_monthly_snapshot_month"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_id: int = Field(foreign_key="scraping_indicators_snapshot.id", index=True)
    handler: str = Field(max_length=200)
    month: date = Field(index=True)
    posts_bb: int = Field(default=0)
    posts_total: int = Field(default=0)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, nullable=False),
    )

    snapshot: Optional["IndicatorsSnapshot"] = Relationship(back_populates="monthly")
