import pandas as pd

def configure(context):
    context.config("data_path")
    context.config("cairo.locations_path")

def execute(context):
    df = pd.read_csv("{}/{}".format(
        context.config("data_path"), context.config("cairo.locations_path")))
    
    return df
