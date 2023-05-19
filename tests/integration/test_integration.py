import os
import re
import subprocess
import sys
import unittest

EXAMPLES_DIR = os.path.join(os.getcwd(), "examples")
TESTS_DIR = os.path.join(os.getcwd(), "tests")


class TestBasic(unittest.TestCase):
    def setUp(self):
        self._invoke_script(TESTS_DIR, "clean.sh")

    def tearDown(self):
        self._invoke_script(TESTS_DIR, "clean.sh")

    def test_python38(self):
        lambda_name = "python38"
        test_dir = os.path.join(EXAMPLES_DIR, "python3.8", "example")

        # build
        self._invoke_script(test_dir, "build.sh")

        # deploy
        self._invoke_script(test_dir, "deploy.sh")

        # invoke lambda2docker
        output = self._invoke_lambda2docker(lambda_name)
        output_dir = re.findall("/tmp/.+", output)[0]

        # assert dockerfile
        expected_dockerfile = """FROM python:3.8-alpine
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]
CMD ["/data/wrapper_entrypoint.py"]"""

        with open(os.path.join(output_dir, "Dockerfile")) as d:
            dockerfile = d.read()

        assert dockerfile == expected_dockerfile

        # assert requirements
        expected_requirements = """requests==2.30.0
"""

        with open(os.path.join(output_dir, "src", "requirements.txt")) as r:
            requirements = r.read()

        assert set(requirements.splitlines()) == set(expected_requirements.splitlines())

        # invoke lambda2docker with flavor
        output = self._invoke_lambda2docker(lambda_name, "slim")
        output_dir = re.findall("/tmp/.+", output)[0]

        # assert dockerfile
        expected_dockerfile = """FROM python:3.8-slim
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]
CMD ["/data/wrapper_entrypoint.py"]"""

        with open(os.path.join(output_dir, "Dockerfile")) as d:
            dockerfile = d.read()

        assert dockerfile == expected_dockerfile

    def test_python38_with_layer(self):
        lambda_name = "python38-with-layer"
        test_dir = os.path.join(EXAMPLES_DIR, "python3.8", "example_with_layer")

        # build
        self._invoke_script(test_dir, "build.sh")

        # deploy
        self._invoke_script(test_dir, "deploy.sh")

        # invoke lambda2docker
        output = self._invoke_lambda2docker(lambda_name)
        output_dir = re.findall("/tmp/.+", output)[0]

        # assert dockerfile
        expected_dockerfile = """FROM python:3.8-alpine
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]
CMD ["/data/wrapper_entrypoint.py"]"""

        with open(os.path.join(output_dir, "Dockerfile")) as d:
            dockerfile = d.read()

        assert dockerfile == expected_dockerfile

        # assert requirements
        expected_requirements = """asyncio==3.4.3
boto3==1.26.133
pyparsing==3.0.9
jellyfish==0.11.2
requests==2.30.0
"""

        with open(os.path.join(output_dir, "src", "requirements.txt")) as r:
            requirements = r.read()

        assert set(requirements.splitlines()) == set(expected_requirements.splitlines())

    def test_python38_with_layers(self):
        lambda_name = "python38-with-layers"
        test_dir = os.path.join(EXAMPLES_DIR, "python3.8", "example_with_layers")

        # build
        self._invoke_script(test_dir, "build.sh")

        # deploy
        self._invoke_script(test_dir, "deploy.sh")

        # invoke lambda2docker
        output = self._invoke_lambda2docker(lambda_name)
        output_dir = re.findall("/tmp/.+", output)[0]

        # assert dockerfile
        expected_dockerfile = """FROM python:3.8-alpine
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]
CMD ["/data/wrapper_entrypoint.py"]"""

        with open(os.path.join(output_dir, "Dockerfile")) as d:
            dockerfile = d.read()

        assert dockerfile == expected_dockerfile

        # assert requirements
        expected_requirements = """asyncio==3.4.3
boto3==1.26.133
pyparsing==3.0.9
jellyfish==0.11.2
requests==2.30.0
lxml==4.9.2
"""

        with open(os.path.join(output_dir, "src", "requirements.txt")) as r:
            requirements = r.read()

        assert set(requirements.splitlines()) == set(expected_requirements.splitlines())

    def _invoke_script(self, script_path, script_filename):
        try:
            subprocess.run(["bash", script_filename], check=True, cwd=script_path)

        except subprocess.CalledProcessError as e:
            print({e.stderr})
            sys.exit(e.returncode)

    def _invoke_lambda2docker(self, lambda_name, flavor=None):
        try:
            if flavor is None:
                output = subprocess.run(
                    [
                        "lambda2docker",
                        "--lambda-name",
                        lambda_name,
                        "--region",
                        "us-east-1",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                output = subprocess.run(
                    [
                        "lambda2docker",
                        "--lambda-name",
                        lambda_name,
                        "--flavor",
                        flavor,
                        "--region",
                        "us-east-1",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
        except subprocess.CalledProcessError as e:
            print(
                f"subprocess.CalledProcessError: Command '['lambda2docker']' errored: {e.output} {e.stdout}, {e.stderr}"
            )
            sys.exit(e.returncode)
        except Exception as e:
            print(e.__str__())
            sys.exit(e.returncode)
        return output.stdout
