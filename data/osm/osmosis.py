import subprocess as sp
import shutil

def configure(context):
    context.config("osmosis_binary", "osmosis")

def run(context, arguments = [], cwd = None):
    """
        This function calls osmosis.
    """
    # Make sure there is a dependency
    context.stage("data.osm.osmosis")

    if cwd is None:
        cwd = context.path()

    command_line = [
        context.config("osmosis_binary")
    ] + arguments

    return_code = sp.check_call(command_line, cwd = cwd)

    if not return_code == 0:
        raise RuntimeError("Osmosis return code: %d" % return_code)

def validate(context):
    if shutil.which(context.config("osmosis_binary")) == "":
        raise RuntimeError("Cannot find Osmosis binary at: %s" % context.config("osmosis_binary"))

    if not b"0.48." in sp.check_output([
        context.config("osmosis_binary"),
        "-v"
    ], stderr = sp.STDOUT):
        print("WARNING! Osmosis of at least version 0.48.x is recommended!")

def execute(context):
    pass
