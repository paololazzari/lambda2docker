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

# package layer 1
pip install --target ./layerpackage asyncio==3.4.3 requests==2.30.0 &> /dev/null
cd layerpackage
zip -r ../layer1-package.zip . &> /dev/null
cd ..

rm -rf ./layerpackage

# package layer 2
pip install --target ./layerpackage pyparsing==3.0.9 boto3==1.26.132 lxml==4.9.2 &> /dev/null
cd layerpackage
zip -r ../layer2-package.zip . &> /dev/null
cd ..

popd
