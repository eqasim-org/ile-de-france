import pandas as pd
import Levenshtein
import tqdm
import numpy as np
import geopandas as gpd

"""
This stage matches the SIRENE enterprise database with address data. While
SIRENE only contains addresses of all enterprises in written form, the BD-TOPO
data set contians all addresses in France in written form, linked to a specific
coordinate. This stage now matched SIRENE and BD-TOPO by address such that a
coordinate is available for SIRENE.

After applying some systematic transformations on the street names of both
data sets, matching is possible exactly for most addresses. However, some
vary slightly so we try to match them to the available street names in their
respective commune by minimizing the Levenshtein distance between the street
name in question and the available ones.

Finally, some SIRENE observations must be filtered out, because they cannot be
matched to a coordinate.

Note that matching only is performed on "[NUMBER] [STREET NAME] [COMMUNE]", while additional
information would be available, such as an addendum to the number, like "5bis".
However, this introduces additional discrepancies between the data set while not
heavily affecting the quality of the location of the enterprises.

TOOD: Can / should we match by post code?
TODO: Should we match by departement instead of commune?

We have the problem here that the commune noted down in SIRENE may not be in
line with our IRIS system. We could also limit the time of the SIRET observations
with their last update to one that fits with our IRIS system.
"""

def configure(context):
    context.stage("data.sirene.cleaned")
    context.stage("data.bdtopo.cleaned")
    context.stage("data.spatial.municipalities")

def execute(context):
    df_sirene = context.stage("data.sirene.cleaned")
    df_bdtopo = context.stage("data.bdtopo.cleaned")
    context.set_info("initial_count", len(df_sirene))

    print("Finding addresses by exact match with street, number and commune ...")

    # First, perform the exact matching
    df_matched = pd.merge(
        df_sirene[["street", "number", "commune_id", "minimum_employees", "maximum_employees", "ape", "siret", "law_status"]],
        df_bdtopo[["street", "number", "commune_id", "geometry"]],
        how = "left", on = ["street", "number", "commune_id"]
    ).drop_duplicates("siret")

    f_missing = df_matched["geometry"].isna()
    df_valid = df_matched[~f_missing].copy()
    df_valid["status"] = 0

    matched_count = np.count_nonzero(~f_missing)
    print("   ... matched %d/%d (%.2f%%)." % (
        matched_count, len(df_sirene), 100 * matched_count / len(df_sirene)
    ))
    context.set_info("exact_count", matched_count)

    # Second, try name matching (without commune) for the ones that could not
    # be matched. This can happen if communes have merged or separated. We
    # need to find the correct commune for them afterwards.

    print("Finding addresses by exact match with street, number without commune ...")

    df_missing = df_matched[f_missing].copy()

    df_matched = pd.merge(
        df_missing[["street", "number", "commune_id", "minimum_employees", "maximum_employees", "ape", "siret", "law_status"]],
        df_bdtopo[["street", "number", "geometry"]],
        how = "left", on = ["street", "number"]
    ).drop_duplicates("siret")

    f_missing = df_matched["geometry"].isna()

    df_partial = df_matched[~f_missing].copy()
    df_partial["status"] = 1
    df_partial["commune"] = "undefined"
    df_partial["commune"] = df_partial["commune"].astype("category")

    matched_count = np.count_nonzero(~f_missing)
    print("   ... matched %d/%d (%.2f%%)." % (
        matched_count, len(df_missing), 100 * matched_count / len(df_missing)
    ))
    context.set_info("no_municipality_count", matched_count)

    # Merge data sets
    df_valid = pd.concat([df_valid, df_partial])
    del df_partial

    # Third, perform matching by Levenshtein distance
    print("Finding addresses by commune and Levenshtein distance ...")

    df_missing = df_matched[f_missing].copy()
    del df_matched

    commune_ids = set(df_missing["commune_id"].unique())
    LEVENSHTEIN_THRESHOLD = 5

    missing_count = 0
    fixed_count = 0

    for commune_id in context.progress(commune_ids, total = len(commune_ids), label = "Fixing missing addresses by Levenshtein distance ..."):
        df_local_bdtopo = df_bdtopo[df_bdtopo["commune_id"] == commune_id]

        if len(df_local_bdtopo) > 0:
            f_commune = df_missing["commune_id"] == commune_id
            df_local_sirene = df_missing[f_commune]

            candidate_streets = set(df_local_bdtopo["street"].unique())
            missing_streets = set(df_local_sirene["street"].unique())
            candidate_streets = list(candidate_streets)

            missing_count += len(missing_streets)

            for missing_street in missing_streets:
                distances = np.array([Levenshtein.distance(missing_street, c) for c in candidate_streets])
                index = np.argmin(distances)

                if distances[index] <= LEVENSHTEIN_THRESHOLD:
                    f = f_commune & (df_missing["street"] == missing_street)
                    df_missing.loc[f, "street"] = candidate_streets[index]
                    fixed_count += 1

    print("Fixed %d/%d (%.2f%%) missing streets by Levenshtein distance" % (
        fixed_count, missing_count, 100 * fixed_count / missing_count
    ))
    context.set_info("levenshtein_count", fixed_count)

    df_fixed = pd.merge(
        df_missing[["street", "number", "commune_id", "minimum_employees", "maximum_employees", "ape", "siret", "law_status"]],
        df_bdtopo[["street", "number", "commune_id", "geometry"]],
        how = "left", on = ["street", "number", "commune_id"]
    ).drop_duplicates("siret")

    f_missing = df_fixed["geometry"].isna()

    matched_count = np.count_nonzero(~f_missing)
    print("... matched %d/%d (%.2f%%) among previously missing ones" % (
        matched_count, len(df_fixed), 100 * matched_count / len(df_fixed)
    ))

    df_fixed = df_fixed[~f_missing].copy()
    df_fixed["status"] = 2

    # Merge data sets
    df_valid = pd.concat([df_valid, df_fixed])
    del df_fixed

    df_valid = gpd.GeoDataFrame(df_valid, crs = "EPSG:2154")

    print("In summary, %d/%d (%.2f%%) SIRENE observations were matched to an address" % (
        len(df_valid), len(df_sirene), 100 * len(df_valid) / len(df_sirene)
    ))

    # Re-assigning commune for all observations
    print("Re-assigning commune for all observations ...")
    df_municipalities = context.stage("data.spatial.municipalities")

    before_count = len(df_valid)
    del df_valid["commune_id"]
    df_valid = gpd.sjoin(df_valid, df_municipalities[["geometry", "commune_id"]], op = "within")
    del df_valid["index_right"]
    after_count = len(df_valid)
    print("... remaining %d/%d observations (%.2f%%)" % (after_count, before_count, 100.0 * after_count / before_count))

    # Check that at least 90% got matched, otherwise something is wrong
    assert after_count / before_count > 0.9

    return df_valid
