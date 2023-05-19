#!/bin/bash

set -e

aws lambda list-functions --region us-east-1 --query 'Functions[].FunctionName' --output text | tr "\t" "\n" | xargs -I {} aws lambda delete-function --region us-east-1 --function-name {}
aws lambda list-layer-versions --layer-name python38layer --query "LayerVersions[].Version" --output text | tr "\t" "\n" | xargs -I {} aws lambda delete-layer-version --layer-name python38layer --version-number {}
aws lambda list-layer-versions --layer-name python38layer1 --query "LayerVersions[].Version" --output text | tr "\t" "\n" | xargs -I {} aws lambda delete-layer-version --layer-name python38layer1 --version-number {}
aws lambda list-layer-versions --layer-name python38layer2 --query "LayerVersions[].Version" --output text | tr "\t" "\n" | xargs -I {} aws lambda delete-layer-version --layer-name python38layer2 --version-number {}