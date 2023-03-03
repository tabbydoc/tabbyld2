from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("VERSION", "r", encoding="utf-8") as f:
    version = f.read()

setup(
    name="tabbyld2",
    version=version,
    description="Software for semantic interpretation of tables and knowledge graph generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nikita O. Dorodnykh",
    author_email="dorodnyxnikita@gmail.com",
    maintainer="Nikita O. Dorodnykh",
    maintainer_email="dorodnyxnikita@gmail.com",
    packages=find_packages(),
    data_files=[("", ["VERSION"])],
    python_requires=">=3.7",
    license="Apache Software License",
    classifiers=[
        "Development Status :: Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers, Knowledge engineers, System Analytics",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ]
)
