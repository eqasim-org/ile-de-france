import geopandas as gpd

def configure(context):
    context.config("data_path")
    context.config("cairo.locations_path")

def execute(context):
    df_locations = gpd.read_file("{}/{}".format(
        context.config("data_path"), context.config("cairo.locations_path")))
    
    return df_locations[["location_id", "location_type", "geometry"]]
