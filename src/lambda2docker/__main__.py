import argparse
import sys

import boto3

from . import validate
from .runtimes.python import python


def main():
    parser = argparse.ArgumentParser("Required arguments")
    parser.add_argument("--lambda-name", required=True)
    parser.add_argument("--region", required=True, default="us-east-1")
    parser.add_argument("--dockerfile-dir", required=False, default=None)
    parser.add_argument("--flavor", required=False, default=None)
    args = parser.parse_args()

    # initialiate boto3 client
    client = boto3.client("lambda", region_name=args.region)

    # get runtime of lambda function
    try:
        runtime = client.get_function(FunctionName=args.lambda_name)["Configuration"][
            "Runtime"
        ]
    except Exception as e:
        print(e.__str__())
        sys.exit(1)

    flavor = args.flavor

    # if flavor isn't specified, use a sensible default according to the runtime
    if flavor is None:
        if "python" in runtime:
            flavor = python.default_flavor

    # validate runtime and flavor
    validate.validate(runtime, flavor)

    if "python" in runtime:
        lambda2docker = python(client, args.lambda_name, args.dockerfile_dir, flavor)
    lambda2docker.run()


if __name__ == "__main__":
    main()
