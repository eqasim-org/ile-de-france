import geopandas as gpd

def configure(context):
    context.config("data_path")
    context.config("cairo.boundary_path")

def execute(context):
    df = gpd.read_file("{}/{}".format(
        context.config("data_path"), context.config("cairo.boundary_path")))
    
    return df[["geometry"]]
