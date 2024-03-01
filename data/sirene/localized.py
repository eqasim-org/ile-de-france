import geopandas as gpd

"""
This stage matches the SIRENE enterprise database with INSEE geolocalized auto detected file

Should we consider using location accuracy variable to optimize process?

"""
def configure(context):
    context.stage("data.sirene.cleaned")
    context.stage("data.sirene.raw_geoloc")
    context.config("crs", 2154)


def execute(context):
    df_sirene = context.stage("data.sirene.cleaned")
    df_siret_geoloc = context.stage("data.sirene.raw_geoloc")


    # merging geographical SIREN file (containing only SIRET and location) with full SIREN file (all variables and processed)
    df_siret_geoloc.set_index(("siret"),inplace=True,verify_integrity=True)
    df_sirene.set_index(("siret"),inplace=True,verify_integrity=True)
    df_siret_geoloc.sort_index(inplace=True)
    df_sirene.sort_index(inplace=True)

    df_sirene = df_sirene.join(df_siret_geoloc,how="left")
    df_sirene.dropna(subset=['x', 'y'],inplace=True)


    # convert to geopandas dataframe with appropriate projection
    df_sirene = gpd.GeoDataFrame(df_sirene, geometry=gpd.points_from_xy(df_sirene.x, df_sirene.y), crs = context.config("crs"))


    return df_sirene
