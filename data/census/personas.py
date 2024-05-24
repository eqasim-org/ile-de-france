import pandas as pd
import os

"""
This stage attaches persona information to the census (RP 2015)
"""

def configure(context):
    context.stage("data.census.cleaned")
    context.config("personas.clustering_path")

def execute(context):
    df = context.stage("data.census.cleaned")

    # Attach 
    df_clusters = pd.read_csv(
        "%s/%s" % (context.config("data_path"), context.config("personas.clustering_path")),
        usecols = ["ID"], sep = ",").rename(columns = {
            "ID": "persona"
        })

    print(len(df_clusters), len(df))
    assert len(df_clusters) == len(df)
    df["persona"] = df_clusters["persona"].values

    return df

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("personas.clustering_path"))):
        raise RuntimeError("Persona cluster data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("personas.clustering_path")))
