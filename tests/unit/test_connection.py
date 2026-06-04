import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:SaludApiYa2026@db.bnqyyrwuiwivggwtpfmx.supabase.co:5432/postgres")
    print("Conectado")
    await conn.close()

asyncio.run(main())