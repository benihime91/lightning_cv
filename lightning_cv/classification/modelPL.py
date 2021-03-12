# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01e_classification.modelPL.ipynb (unless otherwise specified).

__all__ = []

# Cell
from typing import Callable, Dict, List, Optional, Union

import torch
from torch import optim

import hydra
from omegaconf import DictConfig

import matplotlib.pyplot as plt

from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.utilities import rank_zero_only

from ..core.utils.common import default_logger, imshow_tensor
from ..core.optim import create_optimizer
from ..core.schedules import create_scheduler
from .data.transforms import create_transform
from .data.datasets import create_dataset
from .modelling.backbones import create_cnn_backbone
from .modelling.classifiers import create_classifier_head