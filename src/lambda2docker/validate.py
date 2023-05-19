import sys

from .runtimes.python import python

SUPPORTED_RUNTIMES = ["python3.7", "python3.8", "python3.9", "python3.10"]
ERROR_MESSAGE_SUPPORTED_RUNTIMES = ",".join(SUPPORTED_RUNTIMES)


def validate_runtime_supported(runtime):
    if runtime not in SUPPORTED_RUNTIMES:
        print(f"Runtime {runtime} is not supported.")
        print(f"Supported runtimes are: {ERROR_MESSAGE_SUPPORTED_RUNTIMES}")
        sys.exit(1)


def validate_flavor_for_runtime(runtime, flavor):
    if "python" in runtime:
        supported_flavors = python.flavors
        if flavor not in supported_flavors:
            print(f"Flavor {flavor} is not supported for {runtime}")
            print(f"Supported flavors are: {supported_flavors}")
            sys.exit(1)


def validate(runtime, flavor):
    validate_runtime_supported(runtime)
    validate_flavor_for_runtime(runtime, flavor)
