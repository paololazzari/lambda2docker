import glob
import os
import shutil

from ..lambda2docker import lambda2docker


class python(lambda2docker):
    def __init__(self, client, function_name, dockerfile_dir, flavor):
        self.flavor = flavor
        super().__init__(client, function_name, dockerfile_dir)

    def clean_src_dir(self):
        """Clean the lambda source directory"""

        # get source files and source directories which are not dist-info
        src_files = glob.glob(os.path.join(self.src_dir, "*.py"))
        src_dirs = list(
            filter(
                os.path.isdir,
                [
                    os.path.join(self.src_dir, p)
                    for p in os.listdir(self.src_dir)
                    if "dist-info" not in p
                ],
            )
        )

        # parse the RECORD file for each dist
        distdirs = glob.glob(os.path.join(self.src_dir, "*dist-info"))
        for distdir in distdirs:
            with open(os.path.join(distdir, "RECORD")) as f:
                record_file = f.read()

            # remove all files which belong to libraries
            for src_file in src_files:
                src_file_filename = src_file.split(os.sep)[-1]
                if src_file_filename in record_file:
                    os.remove(src_file)
                    src_files.remove(src_file)

            # remove all directories which belong to libraries
            for src_dir in src_dirs:
                for src_dir_filename in glob.iglob(
                    f"{src_dir}{os.sep}**{os.sep}*", recursive=True
                ):
                    is_init_ = src_dir_filename.split(os.sep)[-1] == "__init__.py"
                    if is_init_:
                        p = src_dir_filename.replace(src_dir, "")
                        if p in record_file:
                            try:
                                shutil.rmtree(os.path.join(self.src_dir, src_dir))
                            except:
                                pass

        # delete every dist directory and its corresponding src dir if it exist
        for distdir in distdirs:
            dependency = distdir.split(os.sep)[-1].split("-")[0]
            try:
                shutil.rmtree(os.path.join(self.src_dir, dependency))
            except:
                pass
            shutil.rmtree(distdir)

        # if a bin folder exists and its contents reference other directories, delete them
        try:
            bin_files = os.listdir(os.path.join(self.src_dir, "bin"))
            for bin_file in bin_files:
                if os.path.isdir(os.path.join(self.src_dir, bin_file)):
                    shutil.rmtree(os.path.join(self.src_dir, bin_file))
        except:
            pass

        # remove bin folder if it exists
        try:
            shutil.rmtree(os.path.join(self.src_dir, "bin"))
        except:
            pass

        # remove __pycache__ dir if it exists
        try:
            shutil.rmtree(os.path.join(self.src_dir, "__pycache__"))
        except:
            pass

    def get_dependencies_from_package(self, directory):
        """Extract dependencies from directory"""

        dependencies = []

        # iterate over dist folders to determine whether REQUESTED exists
        distdirs = glob.glob(os.path.join(directory, "*dist-info"))
        for distdir in distdirs:
            if os.path.isfile(os.path.join(distdir, "REQUESTED")):
                dependency = distdir.split(os.sep)[-1].replace(".dist-info", "")
                dependencies.append(dependency)

        self._write_dependencies_to_requirements(directory, dependencies)

    def get_dependencies_from_layers(self):
        """Extract dependencies for lambda layer directories"""

        # get all
        layer_src_dirs = list(
            filter(
                os.path.isdir,
                [
                    os.path.join(self.layer_src_dir, p)
                    for p in os.listdir(self.layer_src_dir)
                ],
            )
        )

        for layer_src_dir in layer_src_dirs:
            self.get_dependencies_from_package(layer_src_dir)

            with open(
                os.path.join(layer_src_dir, "requirements.txt"), "r"
            ) as layer_f, open(
                os.path.join(self.src_dir, "requirements.txt"), "a+"
            ) as lambda_f:
                layer_f.seek(0)
                lambda_f.seek(0)
                layer_requirements = layer_f.read().splitlines()
                lambda_requirements = lambda_f.read().splitlines()

                lambda_requirement_names = [
                    s.split("==")[0] for s in lambda_requirements
                ]

                for layer_requirement in layer_requirements:
                    layer_requirement_name = layer_requirement.split("==")[0]
                    if layer_requirement_name not in lambda_requirement_names:
                        lambda_f.write(layer_requirement + "\n")

    def _write_dependencies_to_requirements(self, directory, dependencies):
        """Write dependencies to requirements.txt"""

        with open(os.path.join(directory, "requirements.txt"), "a+") as f:
            for dependency in dependencies:
                package = "==".join(dependency.split("-"))
                f.write(package + "\n")

    def write_dockerfile(self):
        """Generate Dockerfile"""

        tag = self.runtime.replace(self.handler_prefix, "")
        base_image = f"{self.base_image_prefix}:{tag}-{self.flavor}"
        dockerfile = f"""FROM {base_image}
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]
CMD ["/data/wrapper_entrypoint.py"]"""
        with open(os.path.join(self.output_dir, "Dockerfile"), "w") as f:
            f.writelines(dockerfile)

    def write_wrapper_entrypoint(self):
        """Generate wrapper entrypoint"""

        filename, function_name = self.handler.split(".")
        wrapper_entrypoint = f"""from src.{filename} import {function_name}
{function_name}("","")
"""

        with open(os.path.join(self.output_dir, "wrapper_entrypoint.py"), "w") as f:
            f.writelines(wrapper_entrypoint)

    @classmethod
    @property
    def flavors(self):
        return [
            "bullseye",
            "buster",
            "slim",
            "alpine",
            "slim-buster",
            "slim-bullseye",
        ]

    @classmethod
    @property
    def default_flavor(self):
        return "alpine"

    @property
    def base_image_prefix(self):
        return "python"

    @property
    def handler_prefix(self):
        return "python"
