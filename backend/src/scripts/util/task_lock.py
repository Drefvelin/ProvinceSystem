import asyncio

# Shared async lock to prevent overlapping regenerations
regen_lock = asyncio.Lock()