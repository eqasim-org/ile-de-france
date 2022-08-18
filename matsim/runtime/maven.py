import subprocess as sp
import os, shutil

def configure(context):
    context.config("maven_binary", "mvn")
    context.config("maven_skip_tests", False)

def run(context, arguments = [], cwd = None):
    """
        This function calls Maven.
    """
    # Make sure there is a dependency
    context.stage("matsim.runtime.maven")

    if cwd is None:
        cwd = context.path()

    # Prepare temp folder
    temp_path = "%s/__java_temp" % context.path()
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    vm_arguments = [
        "-Djava.io.tmpdir=%s" % temp_path
    ]

    if context.config("maven_skip_tests"):
        vm_arguments.append("-DskipTests=true")

    command_line = [
        shutil.which(context.config("maven_binary"))
    ] + vm_arguments + arguments

    return_code = sp.check_call(command_line, cwd = cwd)

    if not return_code == 0:
        raise RuntimeError("Maven return code: %d" % return_code)

def validate(context):
    if shutil.which(context.config("maven_binary")) in ["", None]:
        raise RuntimeError("Cannot find Maven binary at: %s" % context.config("maven_binary"))

    if not b"3." in sp.check_output([
        shutil.which(context.config("maven_binary")),
        "-version"
    ], stderr = sp.STDOUT):
        print("WARNING! Maven of at least version 3.x.x is recommended!")

def execute(context):
    pass
