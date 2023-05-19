from setuptools import find_packages, setup

setup(
    name="lambda2docker",
    version="0.1.2",
    description=("Generate a Dockerfile from a lambda function"),
    keywords="aws, lambda, docker",
    author="paololazzari",
    author_email="lazzari.paolok@gmail.com",
    url="https://github.com/paololazzari/lambda2docker",
    license="Apache License 2.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["boto3", "requests"],
    zip_safe=False,
    python_requires=">=3.7, <=4.0",
    entry_points={"console_scripts": ["lambda2docker = lambda2docker.__main__:main"]},
    test_suite="unittest",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
