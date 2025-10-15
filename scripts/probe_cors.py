import asyncio

import httpx

from backend.backend import app


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as c:
        await c.options(
            "/api/ask",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )


if __name__ == "__main__":
    pass
    asyncio.run(main())
