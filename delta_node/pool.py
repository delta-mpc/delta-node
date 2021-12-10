import atexit
import concurrent.futures
import os

__all__ = ["IO_POOL", "WORKER_POOL"]

cpu_count = os.cpu_count()

IO_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count * 5)

WORKER_POOL = concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count)


@atexit.register
def close_pool():
    IO_POOL.shutdown(False)
    WORKER_POOL.shutdown(False)
