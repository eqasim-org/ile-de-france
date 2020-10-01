import shapely.geometry as geo
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("data.bpe.cleaned")
    context.stage("data.spatial.municipalities")

def execute(context):
    df_locations = context.stage("data.bpe.cleaned")[[
        "enterprise_id", "activity_type", "commune_id", "geometry"
    ]]

    df_locations = df_locations[df_locations["activity_type"] == "education"]
    df_locations = df_locations[["commune_id", "geometry"]].copy()

    # Add education destinations to the centroid of zones that have no other destinations
    df_zones = context.stage("data.spatial.municipalities")

    required_communes = set(df_zones["commune_id"].unique())
    missing_communes = required_communes - set(df_locations["commune_id"].unique())

    print("Adding fake education locations for %d/%d municipalities" % (
        len(missing_communes), len(required_communes)
    ))

    df_added = []

    for commune_id in missing_communes:
        centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

        df_added.append({
            "commune_id": commune_id, "geometry": centroid
        })

    df_added = pd.DataFrame.from_records(df_added)

    # Merge together
    df_locations["fake"] = False
    df_added["fake"] = True

    df_locations = pd.concat([df_locations, df_added])

    # Define identifiers
    df_locations["location_id"] = np.arange(len(df_locations))
    df_locations["location_id"] = "edu_" + df_locations["location_id"].astype(str)

    return df_locations[["location_id", "commune_id", "fake", "geometry"]]
