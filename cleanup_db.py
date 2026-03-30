from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Drop all tables that might exist
    conn.execute(text("DROP TABLE IF EXISTS inventory_transactions CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS inventory_products CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS simple_products CASCADE"))
    conn.commit()
    print("All tables dropped successfully!")