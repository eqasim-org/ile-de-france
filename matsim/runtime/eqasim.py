import subprocess as sp
import os, os.path, shutil

import matsim.runtime.git as git
import matsim.runtime.java as java
import matsim.runtime.maven as maven

def configure(context):
    context.stage("matsim.runtime.git")
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.maven")

    context.config("eqasim_version", "1.3.1")
    context.config("eqasim_branch", "upstream")
    context.config("eqasim_repository", "https://github.com/eqasim-org/eqasim-java.git")
    context.config("eqasim_path", "")

def run(context, command, arguments):
    version = context.config("eqasim_version")

    # Make sure there is a dependency
    context.stage("matsim.runtime.eqasim")

    jar_path = "%s/eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % (
        context.path("matsim.runtime.eqasim"), version
    )
    java.run(context, command, arguments, jar_path)

def execute(context):
    version = context.config("eqasim_version")

    # Normal case: we clone eqasim
    if context.config("eqasim_path") == "":
        # Clone repository and checkout version
        git.run(context, [
            "clone", context.config("eqasim_repository"),
            "--branch", context.config("eqasim_branch"),
            "--single-branch", "eqasim-java",
            "--depth", "1"
        ])

        # Build eqasim
        maven.run(context, ["-Pstandalone", "--projects", "ile_de_france", "--also-make", "package"], cwd = "%s/eqasim-java" % context.path())
        jar_path = "%s/eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % (context.path(), version)

    # Special case: We provide the jar directly. This is mainly used for
    # creating input to unit tests of the eqasim-java package.
    else:
        os.makedirs("%s/eqasim-java/ile_de_france/target" % context.path())
        shutil.copy(context.config("eqasim_path"),
            "%s/eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % (context.path(), version))

    return "eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % version

def validate(context):
    path = context.config("eqasim_path")

    if path == "":
        return True

    if not os.path.exists(path):
        raise RuntimeError("Cannot find eqasim at: %s" % path)

    return os.path.getmtime(path)
