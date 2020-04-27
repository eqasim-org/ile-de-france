import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.neighbors import KDTree
import os

"""
Loads and prepares income distributions by municipality:
- Load data with centiles per municipality
- For those which only provide median: Attach another distribution with most similar median
- For those which are missing: Attach the distribution of the municiality with the nearest centroid
"""

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.zones")

def execute(context):
    # Load income distribution
    df = pd.read_excel(
        "%s/filosofi_2015/FILO_DISP_COM.xls" % context.config("data_path"),
        sheet_name = "ENSEMBLE", skiprows = 5
    )[["CODGEO"] + ["D%d15" % q if q != 5 else "Q215" for q in range(1, 10)]]
    df.columns = ["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
    df["reference_median"] = df["q5"].values

    # Filter out invalid commune names
    df["commune_id"] = pd.to_numeric(df["commune_id"], errors = "coerce")
    df = df[~df["commune_id"].isna()]
    df["commune_id"] = df["commune_id"].astype(int)

    # Filter for all necessary communes
    df_communes = context.stage("data.spatial.zones")
    df_communes = df_communes[df_communes["zone_level"] == "commune"]
    required_ids = set(df_communes["commune_id"])
    df = df[df["commune_id"].isin(required_ids)]

    # Find communes without data
    existing_ids = set(df["commune_id"])
    missing_ids = required_ids - existing_ids
    print("Found %d/%d municipalities that are missing" % (len(missing_ids), len(required_ids)))

    # Find communes without full distribution
    df["is_imputed"] = df["q2"].isna()
    df["is_missing"] = False
    print("Found %d/%d municipalities which do not have full distribution" % (sum(df["is_imputed"]), len(required_ids)))

    # First, find suitable distribution for incomplete cases by finding the one with the most similar median
    incomplete_medians = df[df["is_imputed"]]["q5"].values

    df_complete = df[~df["is_imputed"]]
    complete_medians = df_complete["q5"].values

    indices = np.argmin(np.abs(complete_medians[:, np.newaxis] - incomplete_medians[np.newaxis, :]), axis = 0)

    for k in range(1, 10):
        df.loc[df["is_imputed"], "q%d" % k] = df_complete.iloc[indices]["q%d" % k].values

    # Second, add missing municipalities by neirest neighbor
    # ... build tree of existing communes
    df_existing = df_communes[df_communes["commune_id"].isin(df["commune_id"])]
    coordinates = np.vstack([df_existing["geometry"].centroid.x, df_existing["geometry"].centroid.y]).T
    kd_tree = KDTree(coordinates)

    # ... query tree for missing communes
    df_missing = df_communes[df_communes["commune_id"].isin(missing_ids)]
    coordinates = np.vstack([df_missing["geometry"].centroid.x, df_missing["geometry"].centroid.y]).T
    indices = kd_tree.query(coordinates)[1].flatten()

    # ... build data frame of imputed communes
    df_reconstructed = pd.concat([
        df[df["commune_id"] == df_existing.iloc[index]["commune_id"]]
        for index in indices
    ])
    df_reconstructed["commune_id"] = df_missing["commune_id"].values
    df_reconstructed["is_imputed"] = True
    df_reconstructed["is_missing"] = True

    # ... merge the data frames
    df = pd.concat([df, df_reconstructed])
    assert len(df) == len(df["commune_id"].unique())
    assert len(required_ids - set(df["commune_id"])) == 0

    return df[["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "is_imputed", "is_missing", "reference_median"]]

def validate(context):
    if not os.path.exists("%s/filosofi_2015/FILO_DISP_COM.xls" % context.config("data_path")):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/filosofi_2015/FILO_DISP_COM.xls" % context.config("data_path"))
