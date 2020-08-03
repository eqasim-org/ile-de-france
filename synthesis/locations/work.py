import pandas as pd
import Levenshtein
import tqdm
import numpy as np
import geopandas as gpd

"""
This stage provides a list of work places that serve as potential locations for
work activities. It is derived from the SIRENE enterprise database.

Municipalities which do not have any registered enterprise receive a fake work
place at their centroid to be in line with INSEE OD data.

TODO: We may distribute work places randomly in those municipalities.

TODO: Attention! SIRENE data and the other data sets may not always be in
synch, especially if municipalities have merged in the meantime. Then it can
happen that some municipalities are detected as "not having any enterprise"
while they actually (looking at the coordinates) do have enterprises. We could
re-assign enterprises to the correct municipality. Then agian, it would be
important to check if the OD data is in line with the municipality system
that we are using here. In any case, such mergers only happen for very small
municipalities and should not have a large impact for now.
"""

def configure(context):
    context.stage("data.sirene.localized")
    context.stage("data.spatial.municipalities")

def execute(context):
    df_sirene = context.stage("data.sirene.localized")[[
        "commune_id", "employees", "geometry"
    ]].copy()

    ## Use centroids for municipalities where no work places exist
    df_zones = context.stage("data.spatial.municipalities")
    required_communes = set(df_zones["commune_id"].unique())
    missing_communes = required_communes - set(df_sirene["commune_id"].unique())

    print("Adding work places at the centroid of %d communes without SIRENE observations" % len(missing_communes))

    df_added = []

    for commune_id in missing_communes:
        centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

        df_added.append({
            "commune_id": commune_id, "employees": 1.0, "geometry": centroid,
        })

    df_added = pd.DataFrame.from_records(df_added)

    # Merge together
    df_sirene["fake"] = False
    df_added["fake"] = True

    df_workplaces = pd.concat([df_sirene, df_added])

    # Add work identifier
    df_workplaces["location_id"] = np.arange(len(df_workplaces))
    df_workplaces["location_id"] = "work_" + df_workplaces["location_id"].astype(str)

    return df_workplaces[["location_id", "commune_id", "employees", "geometry"]]
