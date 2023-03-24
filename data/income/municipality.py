import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree
import os
import zipfile

"""
Loads and prepares income distributions by municipality:
- Load data with centiles per municipality
- For those which only provide median: Attach another distribution with most similar median
- For those which are missing: Attach the distribution of the municiality with the nearest centroid
"""

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.municipalities")
    context.config("income_com_path", "filosofi_2019/indic-struct-distrib-revenu-2019-COMMUNES.zip")
    context.config("income_com_xlsx", "FILO2019_DISP_COM.xlsx")
    context.config("income_year", 19)

def execute(context):
    # Load income distribution
    year = str(context.config("income_year"))

    with zipfile.ZipFile("{}/{}".format(
        context.config("data_path"), context.config("income_com_path"))) as archive:
        with archive.open(context.config("income_com_xlsx")) as f:
            df = pd.read_excel(f,
                sheet_name = "ENSEMBLE", skiprows = 5
            )[["CODGEO"] + [("D%d" % q) + year if q != 5 else "Q2" + year for q in range(1, 10)]]
            df.columns = ["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
            df["reference_median"] = df["q5"].values

    # Verify spatial data for education
    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())
    df = df[df["commune_id"].isin(requested_communes)]

    # Find communes without data
    df["commune_id"] = df["commune_id"].astype("category")
    missing_communes = set(df_municipalities["commune_id"].unique()) - set(df["commune_id"].unique())
    print("Found %d/%d municipalities that are missing" % (len(missing_communes), len(requested_communes)))

    # Find communes without full distribution
    df["is_imputed"] = df["q2"].isna()
    df["is_missing"] = False
    print("Found %d/%d municipalities which do not have full distribution" % (sum(df["is_imputed"]), len(requested_communes)))

    # First, find suitable distribution for incomplete cases by finding the one with the most similar median
    incomplete_medians = df[df["is_imputed"]]["q5"].values

    df_complete = df[~df["is_imputed"]]
    complete_medians = df_complete["q5"].values

    indices = np.argmin(np.abs(complete_medians[:, np.newaxis] - incomplete_medians[np.newaxis, :]), axis = 0)

    for k in range(1, 10):
        df.loc[df["is_imputed"], "q%d" % k] = df_complete.iloc[indices]["q%d" % k].values

    # Second, add missing municipalities by neirest neighbor
    # ... build tree of existing communes
    df_existing = df_municipalities[df_municipalities["commune_id"].astype(str).isin(df["commune_id"])] # pandas Bug
    coordinates = np.vstack([df_existing["geometry"].centroid.x, df_existing["geometry"].centroid.y]).T
    kd_tree = KDTree(coordinates)

    # ... query tree for missing communes
    df_missing = df_municipalities[df_municipalities["commune_id"].astype(str).isin(missing_communes)] # pandas Bug

    if len(df_missing) > 0:
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

    # Validation
    assert len(df) == len(df["commune_id"].unique())
    assert len(requested_communes - set(df["commune_id"].unique())) == 0

    return df[["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "is_imputed", "is_missing", "reference_median"]]

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("income_com_path"))):
        raise RuntimeError("Municipality Filosofi data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("income_com_path")))
