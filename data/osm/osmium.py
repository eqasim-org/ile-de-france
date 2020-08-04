import subprocess as sp
import shutil

def configure(context):
    context.config("osmium_binary", "osmium")

def run(context, arguments = [], cwd = None):
    """
        This function calls osmium.
    """
    # Make sure there is a dependency
    context.stage("data.osm.osmium")

    if cwd is None:
        cwd = context.path()

    command_line = [
        context.config("osmium_binary")
    ] + arguments

    return_code = sp.check_call(command_line, cwd = cwd)

    if not return_code == 0:
        raise RuntimeError("Osmium return code: %d" % return_code)

def validate(context):
    if shutil.which(context.config("osmium_binary")) == "":
        raise RuntimeError("Cannot find Osmium binary at: %s" % context.config("osmium_binary"))

    if not b"1.11." in sp.check_output([
        context.config("osmium_binary"),
        "--version"
    ], stderr = sp.STDOUT):
        print("WARNING! Osmium of at least version 1.11.x is recommended!")

def execute(context):
    pass
