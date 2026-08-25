import asyncio
from collections import defaultdict

_map_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

def get_map_lock(map_name: str) -> asyncio.Lock:
    return _map_locks[map_name]
