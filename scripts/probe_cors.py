import asyncio
import httpx
from backend.backend import app

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        r = await c.options(
            "/api/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        print("status:", r.status_code)
        print("body:", r.text)
        print("headers:", dict(r.headers))

if __name__ == "__main__":
    asyncio.run(main())
