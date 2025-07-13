"""Package containing all package manager backends"""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type

from .base import PackageBackend

# Dynamically import all backends to register them
discovered_backends: Dict[str, Type[PackageBackend]] = {}

# Iterate over the subdirectories (linux, macos, windows)
for subdir_info in pkgutil.iter_modules([str(Path(__file__).parent)]):
    if not subdir_info.ispkg:
        continue

    subdir_path = Path(__file__).parent / subdir_info.name
    subdir_name = subdir_info.name

    # Iterate over modules within each subdirectory
    for module_info in pkgutil.iter_modules([str(subdir_path)]):
        module_name = f".{subdir_name}.{module_info.name}"
        module = importlib.import_module(module_name, package=__name__)

        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, PackageBackend)
                and attribute is not PackageBackend
                and not getattr(attribute, "name", "").startswith("_")
            ):
                if attribute.name in discovered_backends:
                    raise ImportError(
                        f"Duplicate backend name '{attribute.name}' found. "
                        "Backend names must be unique."
                    )
                discovered_backends[attribute.name] = attribute

# Re-export for easier imports
__all__ = ["PackageBackend", "discovered_backends"]
