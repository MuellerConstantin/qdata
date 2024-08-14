# !/usr/bin/env python3

"""
Contains build automation tasks for the project.
"""

import os
import platform
import shutil
from invoke import task

LINTER = "pylint"
TEST_RUNNER = "pytest"
COMPILER = "nuitka" if platform.system() == "Windows" else "nuitka3"
RESOURCE_COMPILER = "pyside6-rcc"
INTERPRETER = "python" if platform.system() == "Windows" else "python3"

@task(name="test")
def test(ctx):
    """
    Run the test suite.
    """
    ctx.run(f"{TEST_RUNNER}")

@task(name="lint")
def lint(ctx):
    """
    Lint the project.
    """
    ctx.run(f"{LINTER} qdata")

@task(name="resources")
def resources(ctx):
    """
    Build the resources.
    """
    ctx.run(f"{RESOURCE_COMPILER} -o qdata/resources.py resources/resources.qrc")

@task(name="clean")
def clean(ctx):
    # pylint: disable=unused-argument
    """
    Clean the build artifacts.
    """
    if os.path.exists("qdata.build"):
        shutil.rmtree("qdata.build")

    if os.path.exists("qdata.dist"):
        shutil.rmtree("qdata.dist")

@task(name="build", pre=[clean, resources])
def build(ctx):
    # pylint: disable=line-too-long
    """
    Build the project to a standalone executable.
    """
    ctx.run(f"{COMPILER} --plugin-enable=pyside6 --windows-console-mode=disable --windows-icon-from-ico=./resources/favicons/favicon-dark.ico --include-data-files=./LICENSE.md=LICENSE.md --include-data-files=./LICENSE-Apache-2.0.md=LICENSE-Apache-2.0.md --include-data-dir=./resources=resources --standalone qdata")

@task(name="run", pre=[resources])
def run(ctx):
    """
    Run the project in development mode.
    """
    ctx.run(f"{INTERPRETER} -m qdata")
