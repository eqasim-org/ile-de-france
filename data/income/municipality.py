import numpy as np
import pandas as pd
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
    context.stage("data.spatial.municipalities")
    context.config("income_com_path", "filosofi_2019/FILO2019_DISP_COM.xlsx")
    context.config("income_year", 19)

FILOSOFI_ATTRIBUTES = [
        {
            "name": "all",
            "modalities": [
                {"name": "all", "sheet": "ENSEMBLE", "col_pattern": ""},
            ],
        },
        {
            "name": "size",
            "modalities": [
                {"name": "1_pers", "sheet": "TAILLEM_1", "col_pattern": "TME1"},
                {"name": "2_pers", "sheet": "TAILLEM_2", "col_pattern": "TME2"},
                {"name": "3_pers", "sheet": "TAILLEM_3", "col_pattern": "TME3"},
                {"name": "4_pers", "sheet": "TAILLEM_4", "col_pattern": "TME4"},
                {"name": "5_pers_or_more", "sheet": "TAILLEM_5", "col_pattern": "TME5"},
            ],
        },
        {
            "name": "family_comp",
            "modalities": [
                {"name": "Single_man", "sheet": "TYPMENR_1", "col_pattern": "TYM1"},
                {"name": "Single_wom", "sheet": "TYPMENR_2", "col_pattern": "TYM2"},
                {"name": "Couple_without_child", "sheet": "TYPMENR_3", "col_pattern": "TYM3"},
                {"name": "Couple_with_child", "sheet": "TYPMENR_4", "col_pattern": "TYM4"},
                {"name": "Single_parent", "sheet": "TYPMENR_5", "col_pattern": "TYM5"},
                {"name": "complex_hh", "sheet": "TYPMENR_6", "col_pattern": "TYM6"},
            ],
        },
        # {
        #     "name": "age",
        #     "modalities": [
        #         {"name": "0_29", "sheet": "TRAGERF_1", "col_pattern": "AGE1"},
        #         {"name": "30_39", "sheet": "TRAGERF_2", "col_pattern": "AGE2"},
        #         {"name": "40_49", "sheet": "TRAGERF_3", "col_pattern": "AGE3"},
        #         {"name": "50_59", "sheet": "TRAGERF_4", "col_pattern": "AGE4"},
        #         {"name": "60_74", "sheet": "TRAGERF_5", "col_pattern": "AGE5"},
        #         {"name": "75_or_more", "sheet": "TRAGERF_6", "col_pattern": "AGE6"},
        #     ],
        # },
        # {
        #     "name": "ownership",
        #     "modalities": [
        #         {"name": "Owner", "sheet": "OCCTYPR_1", "col_pattern": "TOL1"},
        #         {"name": "Tenant", "sheet": "OCCTYPR_2", "col_pattern": "TOL2"},
        #     ],
        # },
        # {
        #     "name": "income_source",
        #     "modalities": [
        #         {"name": "Salary", "sheet": "OPRDEC_1", "col_pattern": "OPR1"},
        #         {"name": "Unemployment", "sheet": "OPRDEC_2", "col_pattern": "OPR2"},
        #         {"name": "Independent", "sheet": "OPRDEC_3", "col_pattern": "OPR3"},
        #         {"name": "Pension", "sheet": "OPRDEC_4", "col_pattern": "OPR4"},
        #         {"name": "Property", "sheet": "OPRDEC_5", "col_pattern": "OPR5"},
        #         {"name": "None", "sheet": "OPRDEC_6", "col_pattern": "OPR6"},
        #     ],
        # },
    ]

def _read_filosofi_attributes(filosofi_sheets, year, communes):

    concat_list = []
    for attribute in FILOSOFI_ATTRIBUTES:
        if attribute["name"] == "all":
            continue

        for modality in attribute["modalities"]:
            sheet = modality["sheet"]
            col_pattern = modality["col_pattern"]

            data = _read_distributions_from_filosofi(filosofi_sheets, year, sheet, col_pattern, attribute["name"], modality["name"], communes)

            concat_list.append(data)

    df = pd.concat(concat_list)

    # Validation
    # assert len(FILOSOFI_ATTRIBUTES) == len(df["attribute"].unique())
    # assert len(filosofi_sheets) == len(df["modality"].unique())

    return df[
        [
            "commune_id",
            "q1",
            "q2",
            "q3",
            "q4",
            "q5",
            "q6",
            "q7",
            "q8",
            "q9",
            "reference_median",
            "attribute",
            "modality",
        ]
    ]

def _read_filosofi_excel(filepath, attributes):


    # build full list of sheets
    sheet_list = []
    for attribute in attributes:
        sheet_list = sheet_list + [x["sheet"] for x in attribute["modalities"]]

    # read all needed sheets
    excel_df = pd.read_excel(
        filepath,
        sheet_name=sheet_list,
        skiprows=5,
    )

    return excel_df

def _read_distributions_from_filosofi(filosofi_sheets, year, sheet, col_pattern, attribute, modality, communes=None):

    # Load income distribution
    data = filosofi_sheets[sheet][
        ["CODGEO"]
        + [
            "%sD%d" % (col_pattern, q) + year if q != 5 else col_pattern + "Q2" + year
            for q in range(1, 10)
        ]
        ]
    data.columns = ["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
    data["reference_median"] = data["q5"]
    data["modality"] = modality
    data["attribute"] = attribute

    if communes is not None:
        data = data[data["commune_id"].isin(communes)]

    return data


def execute(context):
    # Load income distribution
    year = str(context.config("income_year"))

    # Verify spatial data for education
    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())

    excel_df = _read_filosofi_excel("%s/%s" % (context.config("data_path"), context.config("income_com_path")), FILOSOFI_ATTRIBUTES)

    df = _read_distributions_from_filosofi(excel_df, year, "ENSEMBLE", "", "all", "all", requested_communes)

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

    df_with_attributes = _read_filosofi_attributes(excel_df, year, requested_communes)

    df_with_attributes["is_imputed"] = False
    df_with_attributes["is_missing"] = False

    df = pd.concat([df, df_with_attributes])

    df = df[["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "attribute", "modality", "is_imputed", "is_missing", "reference_median"]]

    return df

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("income_com_path"))):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("income_com_path")))
