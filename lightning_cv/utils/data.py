# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00b_utils.data.ipynb (unless otherwise specified).

__all__ = ['logger', 'Urls', 'download_data', 'pil_loader', 'cv2_loader', 'folder2df', 'stratify_df']

# Cell
import os
import cv2
from PIL import Image
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedKFold
from fastcore.all import ifnone, delegates

from torchvision.datasets.utils import download_and_extract_archive
from torchvision.datasets.folder import IMG_EXTENSIONS

from .common import default_logger

# Cell
# export
# initalize logger
logger = default_logger()

# Cell
# copy from : https://github.com/fastai/fastai/blob/master/nbs/04_data.external.ipynb
# a thin wrapper over the original fastai.URLs
class Urls:
    "Global constants for dataset and model URLs."
    LOCAL_PATH = os.path.abspath(str(Path.cwd() / "data"))
    DOGS = "https://storage.googleapis.com/mledu-datasets/cats_and_dogs_filtered.zip"
    BEES = "https://download.pytorch.org/tutorial/hymenoptera_data.zip"

# Cell
@delegates(download_and_extract_archive)
def download_data(url: str, data_path: str = None, **kwargs):
    "downloads and extracts the data at `Urls.LOCAL_PATH` if datapath is None"
    data_path = ifnone(data_path, Urls.LOCAL_PATH)
    os.makedirs(os.path.abspath(Urls.LOCAL_PATH), exist_ok=True)
    download_and_extract_archive(url, os.path.abspath(Urls.LOCAL_PATH), **kwargs)
    logger.info(f"Data downloaded to {Path(data_path)}")

# Cell
def pil_loader(path) -> Image.Image:
    "loads an image using PIL, mainly used for torchvision transformations"
    with open(path, "rb") as f:
        img = Image.open(f)
        return img.convert("RGB")

# Cell
def cv2_loader(path) -> Image.Image:
    "loads an image using cv2, mainly used for albumentations transformations"
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Cell
def folder2df(folder: str, extension: list = None, shuffle: bool = False):
    "parses all the images in a folder into a pandas dataframe."
    extensions = ifnone(extension, IMG_EXTENSIONS)

    image_list  = []
    target_list = []

    for f in os.listdir(folder):
        curr_path = os.path.join(folder, f)
        if os.path.isdir(curr_path):
            for image in os.listdir(curr_path):
                image_path = os.path.join(curr_path, image)
                image_tgt  = f
                if image_path.lower().endswith(extensions):
                    image_list.append(image_path)
                    target_list.append(image_tgt)

    logger.info(f"Found {len(image_list)} files belonging to {len(set(target_list))} classes.")
    dataframe = pd.DataFrame()
    dataframe["image_id"] = image_list
    dataframe["target"]   = target_list
    if shuffle: dataframe = dataframe.sample(frac=1).reset_index(inplace=False, drop=True)
    return dataframe

# Cell
@delegates(StratifiedKFold)
def stratify_df(df: pd.DataFrame, y: str = None, fold_col: str = None, shuffle: bool = False, **kwargs):
    """makes stratified folds in `df`. The Id of the OOF Validation
    fold will be inserted in `fold_col`. `y` is the name of the column to
    the dependent variable.
    """
    # preserve the original copy of the dataframe
    data = df.copy()
    skf  = StratifiedKFold(**kwargs)
    fold_col = ifnone(fold_col, "kfold")

    ys = data[y]
    data[fold_col] = -1

    for i, (train_index, test_index) in enumerate(skf.split(X=data, y=ys)):
        data.loc[test_index, "kfold"] = i

    if shuffle:  data = data.sample(frac=1).reset_index(drop=True)
    return data