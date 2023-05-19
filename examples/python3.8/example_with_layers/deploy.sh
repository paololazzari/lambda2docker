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
aws lambda create-function --function-name python38-with-layers --zip-file fileb://lambda-package.zip --role "arn:aws:iam::$ACCOUNT_NUMBER:role/lambda-ex" --runtime python3.8 --handler lambda_function.lambda_handler

# deploy layer 1
aws lambda publish-layer-version --layer-name "python38layer1" \
    --license-info "MIT" \
    --zip-file fileb://layer1-package.zip \
    --compatible-runtimes "python3.8" \
    --query "LayerArn" --output "text"

# deploy layer 2
aws lambda publish-layer-version --layer-name "python38layer2" \
    --license-info "MIT" \
    --zip-file fileb://layer2-package.zip \
    --compatible-runtimes "python3.8" \
    --query "LayerArn" --output "text"

LAYER1_VERSION_ARN=$(aws lambda list-layer-versions --layer-name python38layer1 --query "LayerVersions[].LayerVersionArn" --output text)
LAYER2_VERSION_ARN=$(aws lambda list-layer-versions --layer-name python38layer2 --query "LayerVersions[].LayerVersionArn" --output text)

# associate layers with function
aws lambda update-function-configuration --function-name python38-with-layers \
--layers "$LAYER1_VERSION_ARN" "$LAYER2_VERSION_ARN"

popd