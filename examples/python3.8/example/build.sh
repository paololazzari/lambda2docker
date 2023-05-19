#!/bin/bash

# exit on any error
set -e

working_dir=$(dirname -- "${BASH_SOURCE[0]}")
pushd "$working_dir"

# package lambda
pip install --target ./package -r requirements.txt &> /dev/null
cd package
zip -r ../lambda-package.zip . &> /dev/null
cd ..
zip lambda-package.zip lambda_function.py &> /dev/null
rm -rf package

popd