import pandas as pd

def configure(context):
    context.stage("cairo.locations.candidates")

def execute(context):
    df = pd.DataFrame({ "location_id": [], "geometry": [], "is_work": [] })
    return df, df
