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
    if shutil.which(context.config("git_binary")) == "":
        raise RuntimeError("Cannot find git binary at: %s" % context.config("git_binary"))

    if not b"2." in sp.check_output([
        context.config("git_binary"),
        "--version"
    ], stderr = sp.STDOUT):
        print("WARNING! Git of at least version 2.x.x is recommended!")

def execute(context):
    pass
