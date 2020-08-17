import os

def configure(context):
    context.stage("data.hts.selected")
    context.config("output_path")

"""
This stage writes the selected HTS trips to a reference CSV file to be used
for calibration and validation of the simulation output.
"""

def execute(context):
    df_trips = context.stage("data.hts.selected")[2]
    df_trips.to_csv("%s/reference.csv" % context.config("output_path"), sep = ";", index = False)

def validate(context):
    output_path = context.config("output_path")

    if not os.path.isdir(output_path):
        raise RuntimeError("Output directory does not exist: " + output_path)
