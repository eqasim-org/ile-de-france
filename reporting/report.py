import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

def configure(context):
    context.config("output_path")
    context.config("output_prefix")

    context.stage("reporting.collectors.spatial")

def execute(context):
    # Collect the information
    data = {
        "spatial": context.stage("reporting.collectors.spatial")
    }

    # Render the report
    environment = Environment(
        loader = FileSystemLoader("{}/templates".format(os.path.dirname(os.path.abspath(__file__)))),
        autoescape = select_autoescape()
    )

    template = environment.get_template("main.html")
    output = template.render(data)

    with open("{}/{}report.html".format(context.config("output_path"), context.config("output_prefix")), "w+") as f:
        f.write(output)
