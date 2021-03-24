import os.path
from setuptools import setup

REQUIRES_PYTHON = ">=3.6.0"

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md"), encoding="utf-8") as fid:
    README = fid.read()

with open(os.path.join(HERE, "requirements.txt")) as fid:
    REQUIREMENTS = [req for req in fid.read().split("\n") if req]

from aiarena21 import __version__

setup(
    name="ai-arena-21",
    version=__version__,
    description="1v1 Game for AIArena competition 2021",
    long_description=README,
    long_description_content_type="text/markdown",
    python_requires=REQUIRES_PYTHON,
    url="https://github.com/monash-programming-team/aiarena21",
    author="Jackson Goerner, Ali Toosi",
    author_email="jgoerner@outlook.com, alitoosi137@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: pygame",
    ],
    packages=["aiarena21"],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "aiarena21=aiarena21.main",
        ]
    },
)
