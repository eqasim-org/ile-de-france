import subprocess as sp

def configure(context):
    context.config("git_binary", "git")

def run(context, arguments = [], cwd = None):
    """
        This function calls git.
    """
    # Make sure there is a dependency
    context.stage("matsim.runtime.git")

    if cwd is None:
        cwd = context.path()

    command_line = [
        context.config("git_binary")
    ] + arguments

    return_code = sp.check_call(command_line, cwd = cwd)

    if not return_code == 0:
        raise RuntimeError("Git return code: %d" % return_code)

def validate(context):
    if not b"2." in sp.check_output([
        context.config("git_binary"),
        "--version"
    ], stderr = sp.STDOUT):
        raise RuntimeError("Git 2.x.x is required for this pipeline.")

def execute(context):
    pass
