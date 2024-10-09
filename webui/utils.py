import inspect
import time
import functools
import string
import random
from typing import Any, Callable
from contextlib import ContextDecorator
from utils_fmt import (
    green,
    blue,
    yellow,
    magenta,
    cyan
)

_SEP_STR: str = "-" * 30


class catch_time(ContextDecorator):
    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        self.time_start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = time.perf_counter() - self.time_start
        self.readout = f"'{self.message}' took: {self.elapsed:.3f} seconds"
        print(self.readout)


def get_module_of_type(obj: Any) -> str:
    """
    Returns the module from which
    the object type was imported
    """
    module = obj.__module__ if isinstance(obj, type) else type(obj).__module__
    if module == "builtins":
        return "built-in"
    return module


def inspect_func(func: Callable):
    """
    Prints function info
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get function name
        func_name = func.__name__

        # get function signature with parameters
        signature = inspect.signature(func)
        parameters = signature.parameters
        print(_SEP_STR)

        # log passed arguments
        print(f"Calling function '{blue(func_name)}'")
        print("\nArguments passed:")
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            param = parameters[param_name]
            param_annotation = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else "No annotation"
            )

            param_type = type(param_value)
            param_module = get_module_of_type(param_value)
            print(
                f"  {green(param_name)}: {magenta(param_value)} ("
                f"type: {cyan(param_type.__name__)}, "
                f"module: {yellow(param_module)}, "
                f"annotation: {param_annotation})"
            )
        # run function, get result
        result = func(*args, **kwargs)

        # log returning value
        result_type = type(result)
        result_module = get_module_of_type(result)
        return_annotation = (
            signature.return_annotation
            if signature.return_annotation is not inspect.Signature.empty
            else "No annotation"
        )
        print(
            f"\nReturn value: {magenta(result)} ("
            f"type: {cyan(result_type.__name__)}, "
            f"module: {yellow(result_module)}, "
            f"return annotation: {return_annotation})"
        )
        print(f"Finished execution of '{blue(func_name)}'")
        print(_SEP_STR)
        return result
    return wrapper


def generateRandomString(str_length: int = 20) -> str:
    """
    Generates a random string of specified length
    consisting of only ASCII characters.
    """
    chars = (
        random.choice(string.ascii_lowercase)
        for _ in range(str_length)
    )
    return "".join(chars)
