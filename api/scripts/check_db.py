import asyncio
from sqlalchemy import text
from app.db import SessionLocal

async def check():
    async with SessionLocal() as session:
        res = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        ))
        tables = [r[0] for r in res.fetchall()]
        print('Tables count:', len(tables))
        for t in tables:
            cnt = await session.scalar(text(f"SELECT count(*) FROM {t}"))
            print(f"  {t}: {cnt}")

if __name__ == '__main__':
    asyncio.run(check())
