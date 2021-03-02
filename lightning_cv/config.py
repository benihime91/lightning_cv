# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_config.ipynb (unless otherwise specified).

__all__ = ['get_cfg', 'set_global_cfg']

# Cell
from hydra.experimental import compose, initialize, initialize_config_module
from omegaconf import DictConfig
from fastcore.all import delegates

# Cell
@delegates(compose)
def get_cfg(config_name="config", **kwargs) -> DictConfig:
    "Get a copy of the default config"
    with initialize_config_module("lightning_cv.conf"):
        cfg = compose(config_name=config_name, **kwargs)
    return cfg

# Cell
def set_global_cfg(cfg: DictConfig) -> None:
    """
    Let the global config point to the given cfg.
    Assume that the given "cfg" has the key "KEY", after calling
    `set_global_cfg(cfg)`, the key can be accessed by:
    ```python
        from .config import global_cfg
        print(global_cfg.KEY)
    ```
    By using a hacky global config, you can access these configs anywhere,
    without having to pass the config object or the values deep into the code.
    This is a hacky feature introduced for quick prototyping / research exploration.
    """
    global global_cfg
    global_cfg = cfg