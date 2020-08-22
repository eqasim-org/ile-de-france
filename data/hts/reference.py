import os

def configure(context):
    context.stage("data.hts.selected")
    context.config("output_path")

"""
This stage writes the selected HTS trips to a reference CSV file to be used
for calibration and validation of the simulation output.
"""

def execute(context):
    data = context.stage("data.hts.selected")

    data[0].to_csv("%s/hts_households.csv" % context.config("output_path"), sep = ";", index = False)
    data[1].to_csv("%s/hts_persons.csv" % context.config("output_path"), sep = ";", index = False)
    data[2].to_csv("%s/hts_trips.csv" % context.config("output_path"), sep = ";", index = False)

def validate(context):
    output_path = context.config("output_path")

    if not os.path.isdir(output_path):
        raise RuntimeError("Output directory does not exist: " + output_path)
