import subprocess as sp
import os, os.path

import matsim.runtime.git as git
import matsim.runtime.java as java
import matsim.runtime.maven as maven

def configure(context):
    context.stage("matsim.runtime.git")
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.maven")

    context.config("eqasim_version", "1.0.5")

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

    # Clone repository and checkout version
    git.run(context, [
        "clone", "https://github.com/eqasim-org/eqasim-java.git",
        "--branch", "v%s" % version,
        "--single-branch", "eqasim-java",
        "--depth", "1"
    ])

    # Build eqasim
    maven.run(context, ["-Pstandalone", "package"], cwd = "%s/eqasim-java" % context.path())
    jar_path = "%s/eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % (context.path(), version)

    return "eqasim-java/ile_de_france/target/ile_de_france-%s.jar" % version
