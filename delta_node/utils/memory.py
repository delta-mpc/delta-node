import gc

import torch.cuda


def free_memory():
    gc.collect()
    if torch.cuda.is_initialized():
        torch.cuda.empty_cache()
