#!/bin/bash

# exit on any error
set -e

working_dir=$(dirname -- "${BASH_SOURCE[0]}")
pushd "$working_dir"

# get account number
ACCOUNT_NUMBER=$(aws sts get-caller-identity --query Account --output text)

# create lambda role if it does not exist
aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' 2>/dev/null || true 

# deploy lambda function
aws lambda create-function --function-name python38-with-layer --zip-file fileb://lambda-package.zip --role "arn:aws:iam::$ACCOUNT_NUMBER:role/lambda-ex" --runtime python3.8 --handler lambda_function.lambda_handler

# deploy layer
aws lambda publish-layer-version --layer-name "python38layer" \
    --license-info "MIT" \
    --zip-file fileb://layer-package.zip \
    --compatible-runtimes "python3.8" \
    --query "LayerArn" --output "text"

LAYER1_VERSION_ARN=$(aws lambda list-layer-versions --layer-name python38layer --query "LayerVersions[].LayerVersionArn" --output text)

# associate layer with function
aws lambda update-function-configuration --function-name python38-with-layer \
--layers "$LAYER1_VERSION_ARN"

popd