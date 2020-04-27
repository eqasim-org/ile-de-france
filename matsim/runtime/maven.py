import subprocess as sp
import os

def configure(context):
    context.config("maven_binary", "mvn")

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

    command_line = [
        context.config("maven_binary")
    ] + vm_arguments + arguments

    return_code = sp.check_call(command_line, cwd = cwd)

    if not return_code == 0:
        raise RuntimeError("Maven return code: %d" % return_code)

def validate(context):
    assert b"3.6" in sp.check_output([
        context.config("maven_binary"),
        "-version"
    ], stderr = sp.STDOUT)

def execute(context):
    pass
