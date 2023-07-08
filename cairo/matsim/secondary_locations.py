def configure(context):
    context.stage("cairo.locations.candidates")

def execute(context):
    df_locations = context.stage("cairo.locations.candidates")
    df_locations["offers_leisure"] = True
    df_locations["offers_shop"] = True
    df_locations["offers_other"] = True
    return df_locations[["location_id", "geometry", "offers_leisure", "offers_shop", "offers_other"]]
