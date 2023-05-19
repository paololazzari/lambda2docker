import io
import os
import shutil
import sys
import tempfile
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import requests


class lambda2docker(ABC):
    def __init__(self, client, function_name, dockerfile_dir) -> None:
        self.client = client

        # create output directory in tmp location
        try:
            self.output_dir = tempfile.mkdtemp(dir=dockerfile_dir)
        except:
            print("Could not create output directory in {dockerfile_dir}")
            sys.exit(1)

        # create src directories for lambda and for layers
        self.src_dir = os.path.join(self.output_dir, "src")
        self.layer_src_dir = os.path.join(self.output_dir, "layer_src")
        Path(self.src_dir).mkdir()
        Path(self.layer_src_dir).mkdir()

        self.lambda_function = self.client.get_function(FunctionName=function_name)
        self.runtime = self.lambda_function["Configuration"]["Runtime"]
        self.handler = self.lambda_function["Configuration"]["Handler"]

    def __del__(self):
        """Cleanup"""
        shutil.rmtree(self.layer_src_dir)

    def run(self):
        """Run lambda2docker routine"""
        self.get_function_src()
        self.get_dependencies_from_package(self.src_dir)
        self.clean_src_dir()
        self.get_layers_src()
        self.get_dependencies_from_layers()
        self.write_wrapper_entrypoint()
        self.write_dockerfile()
        self.write_output_message()

    def write_output_message(self):
        """Tell user where to find generated artifacts"""
        print("Dockerfile generated in output directory", self.output_dir.__str__())

    def get_function_src(self):
        """Fetch the source code of the lambda function"""
        self._get_src(self.lambda_function["Code"]["Location"], self.src_dir)

    def get_layers_src(self):
        """Fetch the source code of the lambda layers"""
        if "Layers" in self.lambda_function["Configuration"]:
            for layer in self.lambda_function["Configuration"]["Layers"]:
                version = layer["Arn"].split(":")[-1]
                layer_id = ":".join(layer["Arn"].split(":")[0:-1])
                response = self.client.get_layer_version(
                    LayerName=layer_id, VersionNumber=int(version)
                )

                layer_tmp_dir = tempfile.mkdtemp(dir=self.layer_src_dir)
                self._get_src(
                    response["Content"]["Location"],
                    layer_tmp_dir,
                )

    @abstractmethod
    def clean_src_dir():
        """Clean the lambda source directory"""
        pass

    @abstractmethod
    def get_dependencies_from_package():
        """Extract dependencies from directory"""
        pass

    @abstractmethod
    def get_dependencies_from_layers():
        """Extract dependencies for lambda layer directories"""
        pass

    @abstractmethod
    def write_dockerfile(self):
        """Generate Dockerfile"""
        pass

    @abstractmethod
    def write_wrapper_entrypoint(self):
        """Generate wrapper entrypoint"""
        pass

    @abstractmethod
    def flavors():
        """List of available flavors"""
        pass

    @abstractmethod
    def default_flavor():
        """The default flavor"""
        pass

    @abstractmethod
    def base_image_prefix():
        """The prefix of the base image"""

    @abstractmethod
    def handler_prefix():
        """The handler prefix"""
        pass

    def _get_src(self, code_location, output_path):
        """Utility function for downloading and unzipping lambda artefacts"""

        r = requests.get(code_location)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(output_path)
