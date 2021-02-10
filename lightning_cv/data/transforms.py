# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01a_data.transforms.ipynb (unless otherwise specified).

__all__ = ['logger', 'TransformCatalog', 'ImageClassificationTransforms', 'TorchvisionTransform',
           'AlbumentationsTransform', 'ImagenetNoAugmentTransform', 'GenericImageTransform', 'AugTransforms']

# Cell
from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Union, Tuple, Optional
import math

import albumentations as A
from albumentations.pytorch import ToTensorV2

import torch
import torchvision.transforms as T

from timm.data.transforms import RandomResizedCropAndInterpolation, _pil_interp
from timm.data.random_erasing import RandomErasing
from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, DEFAULT_CROP_PCT

from fastcore.all import ifnone, basic_repr
from omegaconf import DictConfig
from hydra.utils import instantiate

from ..utils.common import Registry, default_logger

logger = default_logger()

# Cell
TransformCatalog = Registry('TRANSFORMS')

# Cell
# hide
class ImageClassificationTransforms(ABC):
    "Class representing a data transform abstraction."
    transforms = None
    __repr__ = basic_repr("transforms")

    @abstractmethod
    def __call__(self, image):
        """
        The interface `__call__` is used to transform the input data. It should contain
        the actual implementation of data transform.
        Args:
            image: input image data
        """
        pass

    @classmethod
    def from_config(cls, config: DictConfig):
        return cls(**config)

# Cell
@TransformCatalog.register()
class TorchvisionTransform(ImageClassificationTransforms):
    "base class for creating torchvision transforms"
    def __init__(self, transforms: List):
        self.transforms = T.Compose(transforms)

    def __call__(self, image):
        return self.transforms(image)

    @classmethod
    def from_config(cls, config: DictConfig):
        "Loads in transformations from a `config`"
        transforms = [instantiate(t) for t in config]
        return cls(transforms=transforms)

# Cell
@TransformCatalog.register()
class AlbumentationsTransform(ImageClassificationTransforms):
    "base class for creating albumentations transforms"
    def __init__(self, transforms: List):
        self.transforms = A.Compose(transforms)

    def __call__(self, image):
        return self.transforms(image=image)["image"]

    @classmethod
    def from_config(cls, config: DictConfig):
        "Loads in transformations from a `config`"
        transforms = [instantiate(t) for t in config]
        return cls(transforms=transforms)

# Cell
# modified from : https://github.com/rwightman/pytorch-image-models/blob/master/timm/data/transforms_factory.py
@TransformCatalog.register()
class ImagenetNoAugmentTransform(ImageClassificationTransforms):
    "The default image transform without data augmentation. This can also be used for validation datasets"

    def __init__(self, img_size: Union[Tuple, int] = 224,
                 crop_pct: int = DEFAULT_CROP_PCT,
                 interpolation: str ='bilinear',
                 mean: Union[Tuple, List] = IMAGENET_DEFAULT_MEAN,
                 std: Union[Tuple, List]  = IMAGENET_DEFAULT_STD):

        if isinstance(img_size, tuple):
            assert len(img_size) == 2
            if img_size[-1] == img_size[-2]:
                scale_size = int(math.floor(img_size[0] / crop_pct))
            else: scale_size = tuple([int(x / crop_pct) for x in img_size])
        else: scale_size = int(math.floor(img_size / crop_pct))

        tfl = [
            T.Resize(scale_size, _pil_interp(interpolation)),
            T.CenterCrop(img_size),
            T.ToTensor(),
            T.Normalize(mean=torch.tensor(mean), std=torch.tensor(std))
        ]

        self.transforms = T.Compose(tfl)

    def __call__(self, image):
        return self.transforms(image)

# Cell
# modified from : https://github.com/rwightman/pytorch-image-models/blob/master/timm/data/transforms_factory.py
@TransformCatalog.register()
class GenericImageTransform(ImageClassificationTransforms):
    """
    Default transform for images used in the classification task. This is similar to
    `transforms_imagenet_train` from timm library.
    """

    def __init__(self,
                 img_size: Union[Tuple, int] = 224,
                 scale: Optional[Union[List, Tuple]] = None,
                 ratio: Optional[Union[List, Tuple]] = None,
                 hflip: float = 0.5,
                 vflip: float = 0.5,
                 color_jitter: Optional[Union[List, Tuple, float]] = 0.4,
                 interpolation: str = 'random',
                 re_prob: float = 0.,
                 re_mode: str = 'const',
                 re_count: int = 1,
                 re_num_splits: int = 0,
                 mean: Union[Tuple, List] = IMAGENET_DEFAULT_MEAN,
                 std: Union[Tuple, List] = IMAGENET_DEFAULT_STD):

        # default imagenet scale range
        scale = tuple(ifnone(scale, (0.08, 1.0)))
        # default imagenet ratio range
        ratio = tuple(ifnone(ratio, (3./4., 4./3.)))

        tfl = [RandomResizedCropAndInterpolation(
            img_size, scale=scale, ratio=ratio, interpolation=interpolation)]

        if hflip > 0.:
            tfl += [T.RandomHorizontalFlip(p=hflip)]

        if vflip > 0.:
            tfl += [T.RandomVerticalFlip(p=vflip)]

        if color_jitter is not None:
            if isinstance(color_jitter, (list, tuple)):
                assert len(color_jitter) in (3, 4)
            else:
                # if it's a scalar, duplicate for brightness, contrast, and saturation, no hue
                color_jitter = (float(color_jitter),) * 3

            tfl += [T.ColorJitter(*color_jitter)]

        tfl += [T.ToTensor(), T.Normalize(mean, std)]

        if re_prob > 0.:
            tfl += [
                RandomErasing(re_prob, mode=re_mode, max_count=re_count,
                              num_splits=re_num_splits, device='cpu')
            ]

        self.transforms = T.Compose(tfl)

    def __call__(self, image):
        return self.transforms(image)

# Cell
# inspired from : https://docs.fast.ai/vision.augment.html#aug_transforms
@TransformCatalog.register()
class AugTransforms(ImageClassificationTransforms):
    """
    Utility func to easily create a list of flip, affine, lighting, cutout transforms
    using Albumentations Library.

    * `border_mode` and `interpolation` are OpenCV flag.
    * `do_flip` and `flip_vert` applies Horizontal/ Vertical flips with a prob of 0.5
    * `shift_limit`, `scale_limit`, `max_rotate` are parameters for `albumentations.ShiftScaleRotate`
    * `max_lighting` parameter for `albumentations.HueSaturationValue`
    * `p_shift`, `p_lighting`, `p_cutout` probablities for ShiftScaleRotate, HueSaturationValue & Cutout.
    """

    def __init__(self,
                 img_size: int = 224,
                 scale: Optional[Union[List, Tuple]] = None,
                 ratio: Optional[Union[List, Tuple]] = None,
                 interpolation: int = 1,
                 do_flip: bool = True,
                 flip_vert: bool = False,
                 shift_limit: float = 0.0625,
                 scale_limit: float = 0.1,
                 max_rotate: float = 45,
                 border_mode: int = 4,
                 max_lighting: Optional[Union[List, Tuple, float]] = 0.4,
                 p_shift: float = 0.5,
                 p_lighting: float = 0.75,
                 p_cutout: Optional[float] = 0.5,
                 mean: Union[Tuple, List] = IMAGENET_DEFAULT_MEAN,
                 std: Union[Tuple, List] = IMAGENET_DEFAULT_STD):

        # default imagenet scale range
        scale = tuple(ifnone(scale, (0.08, 1.0)))
        # default imagenet ratio range
        ratio = tuple(ifnone(ratio, (3./4., 4./3.)))

        tfl = [A.RandomResizedCrop(img_size, img_size, scale, ratio, interpolation, p=1.0)]

        if do_flip:
            tfl += [A.HorizontalFlip(p=0.5)]
        if flip_vert:
            tfl += [A.VerticalFlip(p=0.5)]

        tfl += [A.ShiftScaleRotate(shift_limit, scale_limit, max_rotate, interpolation, border_mode, p=p_shift)]

        if max_lighting is not None:
            if isinstance(max_lighting, (list, tuple)):
                assert len(max_lighting) in (3, 4)
            else:
                # if it's a scalar, duplicate for brightness, contrast, and saturation, no hue
                max_lighting = (float(max_lighting),) * 3

            tfl += [A.HueSaturationValue(*max_lighting, p=p_lighting, always_apply=False)]

        if p_cutout is not None:
            tfl += [A.Cutout(p=p_cutout)]

        tfl += [A.Normalize(mean, std, max_pixel_value=255.0, p=1.0), ToTensorV2(p=0.5)]
        self.transforms = A.Compose(tfl)

    def __call__(self, image):
        return self.transforms(image=image)["image"]