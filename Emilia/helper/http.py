import httpx
from aiohttp import ClientSession

session = ClientSession()


http = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(40),
)


async def post(url: str, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data
