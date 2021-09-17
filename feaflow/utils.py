import collections
import importlib
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from pytz import utc

from feaflow import exceptions
from feaflow.abstracts import (
    ComputeUnit,
    FeaflowConfig,
    FeaflowConfigurableComponent,
    FeaflowModel,
    SchedulerConfig,
)


def get_class_from_name(class_name: str):
    if "." not in class_name:
        raise exceptions.ClassImportError(
            class_name,
            "maybe it's a typo or the class name is not a builtin implementation.",
        )
    module_name, class_name = class_name.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except Exception:
        raise exceptions.ClassImportError(class_name)


def create_config_from_dict(
    config_dict: Dict[str, Any], builtin_types: Dict[str, str],
) -> FeaflowConfig:
    assert "type" in config_dict
    type_or_class = str(config_dict["type"]).strip().lower()
    the_class_name = (
        builtin_types[type_or_class]
        if type_or_class in builtin_types
        else type_or_class
    )
    the_class = get_class_from_name(the_class_name)
    assert issubclass(the_class, FeaflowConfigurableComponent)
    the_config = the_class.create_config(**config_dict)
    assert isinstance(the_config, FeaflowConfig)
    return the_config


def create_scheduler_config_from_dict(config_dict: Dict[str, Any]) -> SchedulerConfig:
    if (
        "type" not in config_dict
        or str(config_dict["type"]).strip().lower() == "airflow"
    ):
        from feaflow.airflow import AirflowSchedulerConfig

        config_class = AirflowSchedulerConfig
    else:
        raise NotImplementedError

    return config_class(**config_dict)


def create_instance_from_config(config: FeaflowConfig) -> ComputeUnit:
    return config.impl_cls(config=config)


def split_cols(cols: str) -> List[str]:
    return list(map(str.strip, cols.split(",")))


def create_random_str(short: bool = False) -> str:
    # TODO short
    return f"{int(time.time_ns())}_{random.randint(1000, 9999)}"


def render_template(
    template_source: Any, template_context: Optional[Dict[str, Any]] = None
) -> str:
    from jinja2 import Template

    if template_context is None:
        template_context = {}
    return Template(template_source).render(template_context)


def deep_merge_models(model: FeaflowModel, merge_model: FeaflowModel) -> FeaflowModel:
    assert type(model) == type(merge_model)
    source_dict = merge_model.dict(exclude_defaults=True)
    dest_dict = model.dict(exclude_defaults=True)
    deep_merge_dicts(source_dict, dest_dict)
    return type(model)(**source_dict)


def deep_merge_dicts(_dict: Dict, merge_dict: Dict):
    for k, v in merge_dict.items():
        if (
            k in _dict
            and isinstance(_dict[k], dict)
            and isinstance(merge_dict[k], collections.Mapping)
        ):
            deep_merge_dicts(_dict[k], merge_dict[k])
        else:
            _dict[k] = merge_dict[k]


def make_tzaware(t: datetime) -> datetime:
    if t.utcoffset() is None:
        return t.replace(tzinfo=utc)
    else:
        return t
