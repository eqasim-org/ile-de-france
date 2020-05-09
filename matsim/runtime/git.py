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
    assert b"2.23" in sp.check_output([
        context.config("git_binary"),
        "--version"
    ], stderr = sp.STDOUT)

def execute(context):
    pass
