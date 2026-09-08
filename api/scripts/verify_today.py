import asyncio
import sys
from datetime import date
import uuid
from sqlalchemy import select
from app.db import SessionLocal
from app.models.core import TimeBlock, User

sys.stdout.reconfigure(encoding='utf-8')

async def check():
    async with SessionLocal() as session:
        uid = uuid.UUID('90c338e9-6460-4960-9dfc-596dec17dba8')
        user = await session.get(User, uid)
        print('User:', user.id, user.email, user.settings)
        
        blocks = (await session.execute(
            select(TimeBlock)
            .where(TimeBlock.user_id == uid, TimeBlock.date == date(2026, 9, 7))
            .order_by(TimeBlock.seq)
        )).scalars().all()
        
        print(f"Today Monday (2026-09-07) blocks count: {len(blocks)}")
        for b in blocks:
            start = b.start_resolved.strftime('%H:%M') if b.start_resolved else '??:??'
            end = b.end_resolved.strftime('%H:%M') if b.end_resolved else '??:??'
            print(f"  #{b.seq:02d} | {start} - {end} | {b.activity} | {b.tier} | {b.category} | {b.planned_minutes}m | {b.status}")

if __name__ == '__main__':
    asyncio.run(check())
