#!/bin/bash

# exit on any error
set -e

working_dir=$(dirname -- "${BASH_SOURCE[0]}")
pushd "$working_dir"

# package lambda
pip install --target ./package -r requirements.txt &> /dev/null
cd "package"
zip -r ../lambda-package.zip . &> /dev/null
cd ..
zip lambda-package.zip lambda_function.py &> /dev/null

# package layer
pip install --target ./layerpackage asyncio==3.4.3 requests==2.30.0 &> /dev/null
cd layerpackage
zip -r ../layer-package.zip . &> /dev/null
cd ..

popd
