import atexit
import concurrent.futures
import os
import multiprocessing as mp
import gc


__all__ = ["IO_POOL", "WORKER_POOL", "RUNNER_POOL", "MANAGER", "close"]

cpu_count = os.cpu_count()

IO_POOL = concurrent.futures.ThreadPoolExecutor(
    max_workers=cpu_count * 5 if cpu_count else None
)

WORKER_POOL = concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count)

RUNNER_POOL = concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count)

MANAGER = mp.Manager()

LOG_QUEUE = MANAGER.Queue()


def close():
    gc.collect()
    RUNNER_POOL.shutdown(True)
    WORKER_POOL.shutdown(True)
    IO_POOL.shutdown(True)
    MANAGER.shutdown()
