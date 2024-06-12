import pandas as pd
import os

"""
This stage attaches persona information to the census (RP 2015)
"""

def configure(context):
    context.stage("synthesis.population.projection.reweighted")
    context.stage("data.spatial.codes")

    context.config("personas.clustering_path")

def execute(context):
    df = context.stage("synthesis.population.projection.reweighted")

    # Filter here fore IDF (usually we would only do that in *.filtered)
    df_codes = context.stage("data.spatial.codes")
    requested_departements = df_codes["departement_id"].unique()
    df = df[df["departement_id"].isin(requested_departements)]

    # Attach 
    df_clusters = pd.read_csv(
        "%s/%s" % (context.config("data_path"), context.config("personas.clustering_path")),
        usecols = ["ID"], sep = ",").rename(columns = {
            "ID": "persona"
        })

    assert len(df_clusters) == len(df)
    assert set(range(16)) == set(df["persona"].unique())
    df["persona"] = df_clusters["persona"].values

    return df

def validate(context):
    if not os.path.exists("%s/%s/clusters_2019.csv" % (context.config("data_path"), context.config("personas.input_path"))):
        raise RuntimeError("Persona cluster data is not available")

    return os.path.getsize("%s/%s/clusters_2019.csv" % (context.config("data_path"), context.config("personas.input_path")))
