"""Shared helpers used across the application."""

from importlib import import_module
from pathlib import Path
from typing import TypeVar, cast

from macro.utils.logger import logging


T = TypeVar("T")


def load_exported_instances(
    directory: Path,
    package_name: str,
    base_class: type[T],
) -> list[T]:
    """Instantiate classes exported through ``__all__`` in a plugin directory."""
    instances: list[T] = []

    for file_path in sorted(directory.glob("*.py")):
        if file_path.name == "__init__.py":
            continue

        module_name = f"{package_name}.{file_path.stem}"
        module = import_module(module_name)

        if not hasattr(module, "__all__"):
            logging.warning(
                f"Couldn't load {file_path} since it has no __all__."
            )
            continue

        for class_name in module.__all__:
            exported = getattr(module, class_name)
            if not isinstance(exported, type) or not issubclass(exported, base_class):
                raise TypeError(
                    f"{module_name}.{class_name} must be a subclass of "
                    f"{base_class.__name__}."
                )

            instance = cast(type[T], exported)()
            instances.append(instance)
            logging.info(f"Loaded {class_name} from {file_path}.")

    return instances