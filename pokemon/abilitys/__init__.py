from .abstract_ability import *
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):

    if module_name == "abstract_ability":
        continue
    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            # Add the class to this package's variables
            globals()[attribute_name] = attribute
