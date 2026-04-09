"""create scraping ingestion tables

Revision ID: b5f1e2a9c7d4
Revises: 84e74e67a3c1
Create Date: 2026-04-07
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5f1e2a9c7d4"
down_revision = "84e74e67a3c1"
branch_labels = None
depends_on = None


run_status_enum = sa.Enum(
    "success",
    "partial",
    "failed",
    "unknown",
    name="scraping_run_status",
    native_enum=False,
)
social_platform_enum = sa.Enum(
    "instagram",
    "x",
    "tiktok",
    name="scraping_social_platform",
    native_enum=False,
)
bb_connection_type_enum = sa.Enum(
    "mention",
    "hashtag",
    "mention-hashtag",
    name="scraping_bb_connection_type",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "scraping_sponsors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=True),
        sa.Column("instagram_handle", sa.String(length=160), nullable=True),
        sa.Column("instagram_url", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_row_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_scraping_sponsors_slug"),
        sa.UniqueConstraint("instagram_handle", name="uq_scraping_sponsors_instagram_handle"),
    )
    op.create_index("ix_scraping_sponsors_slug", "scraping_sponsors", ["slug"], unique=False)
    op.create_index(
        "ix_scraping_sponsors_instagram_handle",
        "scraping_sponsors",
        ["instagram_handle"],
        unique=False,
    )

    op.create_table(
        "scraping_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("run_handle", sa.String(length=200), nullable=False),
        sa.Column("out_dir", sa.String(length=1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("since_date", sa.Date(), nullable=True),
        sa.Column("until_date", sa.Date(), nullable=True),
        sa.Column("max_items", sa.Integer(), nullable=True),
        sa.Column("scrape_instagram", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scrape_x", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scrape_tiktok", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("run_status", run_status_enum, nullable=False, server_default="unknown"),
        sa.Column("source_files_hash", sa.String(length=128), nullable=True),
        sa.Column("run_csv_path", sa.String(length=1000), nullable=True),
        sa.Column("run_log_path", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sponsor_id"], ["scraping_sponsors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scraping_runs_sponsor_id", "scraping_runs", ["sponsor_id"], unique=False)
    op.create_index("ix_scraping_runs_started_at", "scraping_runs", ["started_at"], unique=False)
    op.create_index(
        "ix_scraping_runs_sponsor_started_at",
        "scraping_runs",
        ["sponsor_id", "started_at"],
        unique=False,
    )
    op.create_index("ix_scraping_runs_run_status", "scraping_runs", ["run_status"], unique=False)

    op.create_table(
        "scraping_social_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("platform", social_platform_enum, nullable=False),
        sa.Column("post_url", sa.String(length=2000), nullable=False),
        sa.Column("shortcode", sa.String(length=120), nullable=True),
        sa.Column("post_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_date", sa.Date(), nullable=True),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("hashtags_raw", sa.Text(), nullable=True),
        sa.Column("mentions_raw", sa.Text(), nullable=True),
        sa.Column("owner_username", sa.String(length=160), nullable=True),
        sa.Column("is_owner_profile", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("media_type", sa.String(length=80), nullable=True),
        sa.Column("is_collab", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("coauthors_raw", sa.Text(), nullable=True),
        sa.Column("paid_partnership", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("paid_partner", sa.String(length=240), nullable=True),
        sa.Column("location", sa.String(length=400), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("views", sa.Integer(), nullable=True),
        sa.Column("plays_or_views", sa.Integer(), nullable=True),
        sa.Column("replies", sa.Integer(), nullable=True),
        sa.Column("reposts", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("is_bb_mention", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("bb_connection_type", bb_connection_type_enum, nullable=True),
        sa.Column("bb_markers_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_row_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["scraping_runs.id"]),
        sa.ForeignKeyConstraint(["sponsor_id"], ["scraping_sponsors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform",
            "post_url",
            name="uq_scraping_social_posts_platform_post_url",
        ),
    )
    op.create_index("ix_scraping_social_posts_run_id", "scraping_social_posts", ["run_id"], unique=False)
    op.create_index(
        "ix_scraping_social_posts_sponsor_id",
        "scraping_social_posts",
        ["sponsor_id"],
        unique=False,
    )
    op.create_index("ix_scraping_social_posts_platform", "scraping_social_posts", ["platform"], unique=False)
    op.create_index("ix_scraping_social_posts_shortcode", "scraping_social_posts", ["shortcode"], unique=False)
    op.create_index(
        "ix_scraping_social_posts_post_datetime",
        "scraping_social_posts",
        ["post_datetime"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_social_posts_is_bb_mention",
        "scraping_social_posts",
        ["is_bb_mention"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_social_posts_sponsor_platform_post_datetime",
        "scraping_social_posts",
        ["sponsor_id", "platform", "post_datetime"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_social_posts_sponsor_is_bb_mention",
        "scraping_social_posts",
        ["sponsor_id", "is_bb_mention"],
        unique=False,
    )

    op.create_table(
        "scraping_post_hashtags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("hashtag", sa.String(length=160), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["scraping_social_posts.id"]),
        sa.PrimaryKeyConstraint("post_id", "hashtag"),
    )

    op.create_table(
        "scraping_post_mentions",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("mention_handle", sa.String(length=160), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["scraping_social_posts.id"]),
        sa.PrimaryKeyConstraint("post_id", "mention_handle"),
    )

    op.create_table(
        "scraping_post_coauthors",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("coauthor_handle", sa.String(length=160), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["scraping_social_posts.id"]),
        sa.PrimaryKeyConstraint("post_id", "coauthor_handle"),
    )

    op.create_table(
        "scraping_profile_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("platform", social_platform_enum, nullable=False),
        sa.Column("profile_url", sa.String(length=2000), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("username", sa.String(length=160), nullable=True),
        sa.Column("display_name", sa.String(length=240), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("following", sa.Integer(), nullable=True),
        sa.Column("posts_count", sa.Integer(), nullable=True),
        sa.Column("likes_total", sa.Integer(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("external_url", sa.Text(), nullable=True),
        sa.Column("meta_description", sa.Text(), nullable=True),
        sa.Column("og_title", sa.Text(), nullable=True),
        sa.Column("og_description", sa.Text(), nullable=True),
        sa.Column("raw_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["scraping_runs.id"]),
        sa.ForeignKeyConstraint(["sponsor_id"], ["scraping_sponsors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform",
            "profile_url",
            "fetched_at",
            name="uq_scraping_profile_snapshots_platform_url_fetched",
        ),
    )
    op.create_index(
        "ix_scraping_profile_snapshots_run_id",
        "scraping_profile_snapshots",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_profile_snapshots_sponsor_id",
        "scraping_profile_snapshots",
        ["sponsor_id"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_profile_snapshots_platform",
        "scraping_profile_snapshots",
        ["platform"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_profile_snapshots_fetched_at",
        "scraping_profile_snapshots",
        ["fetched_at"],
        unique=False,
    )

    op.create_table(
        "scraping_indicators_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("sponsor_id", sa.Integer(), nullable=False),
        sa.Column("handler", sa.String(length=200), nullable=False),
        sa.Column("generated_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_indicadores_csv_path", sa.String(length=1000), nullable=True),
        sa.Column("source_indicadores_json_path", sa.String(length=1000), nullable=True),
        sa.Column("indicators_csv_flat_json", sa.Text(), nullable=True),
        sa.Column("indicators_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["scraping_runs.id"]),
        sa.ForeignKeyConstraint(["sponsor_id"], ["scraping_sponsors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", name="uq_scraping_indicators_snapshot_run_id"),
    )
    op.create_index(
        "ix_scraping_indicators_snapshot_run_id",
        "scraping_indicators_snapshot",
        ["run_id"],
        unique=True,
    )
    op.create_index(
        "ix_scraping_indicators_snapshot_sponsor_id",
        "scraping_indicators_snapshot",
        ["sponsor_id"],
        unique=False,
    )
    op.create_index(
        "ix_scraping_indicators_snapshot_generated_at_utc",
        "scraping_indicators_snapshot",
        ["generated_at_utc"],
        unique=False,
    )

    op.create_table(
        "scraping_indicators_monthly",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("handler", sa.String(length=200), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("posts_bb", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("posts_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["scraping_indicators_snapshot.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "month",
            name="uq_scraping_indicators_monthly_snapshot_month",
        ),
    )
    op.create_index(
        "ix_scraping_indicators_monthly_snapshot_id",
        "scraping_indicators_monthly",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index("ix_scraping_indicators_monthly_month", "scraping_indicators_monthly", ["month"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scraping_indicators_monthly_month", table_name="scraping_indicators_monthly")
    op.drop_index("ix_scraping_indicators_monthly_snapshot_id", table_name="scraping_indicators_monthly")
    op.drop_table("scraping_indicators_monthly")

    op.drop_index("ix_scraping_indicators_snapshot_generated_at_utc", table_name="scraping_indicators_snapshot")
    op.drop_index("ix_scraping_indicators_snapshot_sponsor_id", table_name="scraping_indicators_snapshot")
    op.drop_index("ix_scraping_indicators_snapshot_run_id", table_name="scraping_indicators_snapshot")
    op.drop_table("scraping_indicators_snapshot")

    op.drop_index("ix_scraping_profile_snapshots_fetched_at", table_name="scraping_profile_snapshots")
    op.drop_index("ix_scraping_profile_snapshots_platform", table_name="scraping_profile_snapshots")
    op.drop_index("ix_scraping_profile_snapshots_sponsor_id", table_name="scraping_profile_snapshots")
    op.drop_index("ix_scraping_profile_snapshots_run_id", table_name="scraping_profile_snapshots")
    op.drop_table("scraping_profile_snapshots")

    op.drop_table("scraping_post_coauthors")
    op.drop_table("scraping_post_mentions")
    op.drop_table("scraping_post_hashtags")

    op.drop_index(
        "ix_scraping_social_posts_sponsor_is_bb_mention",
        table_name="scraping_social_posts",
    )
    op.drop_index(
        "ix_scraping_social_posts_sponsor_platform_post_datetime",
        table_name="scraping_social_posts",
    )
    op.drop_index("ix_scraping_social_posts_is_bb_mention", table_name="scraping_social_posts")
    op.drop_index("ix_scraping_social_posts_post_datetime", table_name="scraping_social_posts")
    op.drop_index("ix_scraping_social_posts_shortcode", table_name="scraping_social_posts")
    op.drop_index("ix_scraping_social_posts_platform", table_name="scraping_social_posts")
    op.drop_index("ix_scraping_social_posts_sponsor_id", table_name="scraping_social_posts")
    op.drop_index("ix_scraping_social_posts_run_id", table_name="scraping_social_posts")
    op.drop_table("scraping_social_posts")

    op.drop_index("ix_scraping_runs_run_status", table_name="scraping_runs")
    op.drop_index("ix_scraping_runs_sponsor_started_at", table_name="scraping_runs")
    op.drop_index("ix_scraping_runs_started_at", table_name="scraping_runs")
    op.drop_index("ix_scraping_runs_sponsor_id", table_name="scraping_runs")
    op.drop_table("scraping_runs")

    op.drop_index("ix_scraping_sponsors_instagram_handle", table_name="scraping_sponsors")
    op.drop_index("ix_scraping_sponsors_slug", table_name="scraping_sponsors")
    op.drop_table("scraping_sponsors")
