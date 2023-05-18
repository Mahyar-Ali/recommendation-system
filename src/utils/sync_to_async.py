import asyncio
import concurrent
from functools import partial, wraps


# To wrap functions into asynchronous code, this is not being used anywhere right now.
# Potential usage is to convert text_cleaning functions into async using this wrapper
def wrap(func, process_exec=False):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        if process_exec:
            with concurrent.futures.ProcessPoolExecutor() as pool:
                return await loop.run_in_executor(pool, func, *args)

        return await loop.run_in_executor(executor, pfunc)

    return run


# Ref: https://dev.to/0xbf/turn-sync-function-to-async-python-tips-58nn
