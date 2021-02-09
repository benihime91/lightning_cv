# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_utils.common.ipynb (unless otherwise specified).

__all__ = ['get_default_logger', 'imshow_tensor', 'generate_random_id']

# Cell
import sys
import uuid
from loguru import logger
import matplotlib.pyplot as plt
from fvcore.common import registry
from fastcore.all import ifnone, delegates
from torchvision.utils import make_grid

# Cell
@delegates(logger.add)
def get_default_logger(format = None, sink = None, **kwargs):
    "create a loguru from `format` and log to `sink`"
    format = ifnone(format, "<level>{level}</level>:<cyan>{name:}</cyan>:{message}")
    sink = ifnone(sink, sys.stdout)
    logger.remove()
    logger.add(sink=sys.stdout, format=format, colorize=True)
    return logger

# Cell
@delegates(make_grid)
def imshow_tensor(inp, title=None, **kwargs):
    """Imshow for Tensor and optionally add a `title`"""
    grid = make_grid(inp, **kwargs)
    grid = grid.permute(1, 2, 0).data.numpy()
    plt.imshow(grid)

    if title is not None:
        plt.title(title)

    plt.pause(0.001)

# Cell
def generate_random_id() -> str:
    "generates a random id"
    idx = uuid.uuid1()
    idx = str(idx).split("-")[0]
    return idx