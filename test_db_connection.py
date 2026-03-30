from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()
        print("✅ Database connected successfully!")
        print(f"PostgreSQL version: {version[0]}")
except Exception as e:
    print("❌ Database connection failed!")
    print(f"Error: {e}")