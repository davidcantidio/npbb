"""Check DB state: alembic_version + key ENUM types."""
import sqlalchemy as sa

URL = "postgresql+psycopg2://postgres.jwiznrbfzhidhrpxtvhl:%40liceDioH%26lena123@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"
engine = sa.create_engine(URL, connect_args={"sslmode": "require"})

with engine.connect() as conn:
    avrows = conn.execute(
        sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")
    ).fetchall()
    print("alembic_version:", [r[0] for r in avrows])

    enum_query = sa.text(
        "SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname"
    )
    enums = conn.execute(enum_query).fetchall()
    print("ENUMs:", [r[0] for r in enums])
