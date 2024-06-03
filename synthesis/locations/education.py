import shapely.geometry as geo
import numpy as np
import pandas as pd
import geopandas as gpd

def configure(context):
    context.stage("data.bpe.cleaned")
    context.stage("data.spatial.municipalities")

def fake_education(missing_communes, c, df_locations, df_zones):
    # Fake education destinations as the centroid of zones that have no other destinations
    print(
        "Adding fake education locations for %d municipalities"
        % (len(missing_communes))
    )

    df_added = []

    for commune_id in sorted(missing_communes):
        centroid = df_zones[df_zones["commune_id"] == commune_id][
            "geometry"
        ].centroid.iloc[0]

        df_added.append({"commune_id": commune_id, "geometry": centroid})

    df_added = gpd.GeoDataFrame(
        pd.DataFrame.from_records(df_added), crs=df_locations.crs
    )
    df_added["fake"] = True
    df_added["TYPEQU"] = c

    return df_added

def execute(context):
    df_locations = context.stage("data.bpe.cleaned")[[
        "enterprise_id", "activity_type", "TYPEQU", "commune_id", "geometry"
    ]]

    df_locations = df_locations[df_locations["activity_type"] == "education"]
    df_locations = df_locations[["TYPEQU", "commune_id", "geometry"]].copy()
    df_locations["fake"] = False

    # Add education destinations to the centroid of zones that have no other destinations
    df_zones = context.stage("data.spatial.municipalities")

    required_communes = set(df_zones["commune_id"].unique())
    # Add education destinations in function of level education
    for c in ["C1", "C2", "C3"]:
        missing_communes = required_communes - set(
            df_locations[df_locations["TYPEQU"].str.startswith(c)]["commune_id"].unique())

        if len(missing_communes) > 0:
            df_locations = pd.concat([df_locations,fake_education(missing_communes, c, df_locations, df_zones)])
    
    # Add education destinations in function of level education
    missing_communes = required_communes - set(df_locations[~(df_locations["TYPEQU"].str.startswith(("C1", "C2", "C3")))]["commune_id"].unique())

    if len(missing_communes) > 0:

        df_locations = pd.concat([df_locations,fake_education(missing_communes, "C4", df_locations, df_zones)])
    
    # Define identifiers
    df_locations["location_id"] = np.arange(len(df_locations))
    df_locations["location_id"] = "edu_" + df_locations["location_id"].astype(str)

    return df_locations[["location_id", "commune_id", "fake", "geometry"]]
