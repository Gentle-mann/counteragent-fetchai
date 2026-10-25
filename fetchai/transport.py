"""Bounded API resolver: no synchronous ledger fallback in message handlers."""
import time
import aiohttp
from uagents.resolver import Resolver, parse_identifier
from uagents.config import ALMANAC_API_URL


class ApiResolver(Resolver):
    def __init__(self):
        self.cache = {}

    async def resolve(self, destination):
        _, _, address = parse_identifier(destination)
        cached = self.cache.get(address)
        if cached and cached[0] > time.monotonic():
            return address, cached[1]
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(ALMANAC_API_URL.rstrip('/') + '/agents/' + address) as response:
                    if response.status != 200:
                        return None, []
                    data = await response.json()
            endpoints = [e['url'] for e in data.get('endpoints', []) if isinstance(e.get('url'), str) and e['url'].startswith(('https://','http://'))][:3]
            if endpoints:
                self.cache[address] = (time.monotonic()+120, endpoints)
                return address, endpoints
        except (aiohttp.ClientError, TimeoutError, ValueError):
            pass
        return None, []
