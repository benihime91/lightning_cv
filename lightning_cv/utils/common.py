# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00a_utils.common.ipynb (unless otherwise specified).

__all__ = ['default_logger', 'imshow_tensor', 'generate_random_id']

# Cell
import sys
import uuid
import matplotlib.pyplot as plt
from fvcore.common.registry import Registry
from fastcore.all import ifnone, delegates
from torchvision.utils import make_grid

# Cell
def default_logger():
    "default logger for the Library"
    from loguru import logger

    __root_name = "lightning_cv"
    __abbrev_name = "Lcv"

    fmt = "<level>{level}</level>:<green>{name:}</green>:{message}"
    logger.remove()
    logger.add(sys.stdout, format=fmt, colorize=True)
    logger = logger.patch(lambda record: record.update(name=record["name"].replace(__root_name, __abbrev_name)))
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