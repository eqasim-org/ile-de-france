from tqdm import tqdm
import pandas as pd
import numpy as np
import simpledbf
import os

"""
Loads raw OD data from French census data.
"""

def configure(context):
    context.stage("data.spatial.codes")
    context.config("data_path")
    context.config("od_pro_path", "rp_2015/FD_MOBPRO_2015.dbf")
    context.config("od_sco_path", "rp_2015/FD_MOBSCO_2015.dbf")

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_communes = df_codes["commune_id"].unique()

    # First, load work

    table = simpledbf.Dbf5("%s/%s" % (context.config("data_path"), context.config("od_pro_path")))
    records = []

    with context.progress(label = "Reading work flows ...", total = table.numrec) as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))

            f = df_chunk["COMMUNE"].isin(requested_communes)
            f |= df_chunk["ARM"].isin(requested_communes)
            f &= df_chunk["DCLT"].isin(requested_communes)

            df_chunk = df_chunk[f]
            df_chunk = df_chunk[["COMMUNE", "ARM", "TRANS", "IPONDI", "DCLT"]]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/work.hdf" % context.cache_path, "movements")

    # Second, load education

    table = simpledbf.Dbf5("%s/%s" % (context.config("data_path"), context.config("od_sco_path")))
    records = []

    with context.progress(label = "Reading education flows ...", total = 4782736) as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))

            f = df_chunk["COMMUNE"].isin(requested_communes)
            f |= df_chunk["ARM"].isin(requested_communes)
            f &= df_chunk["DCETUF"].isin(requested_communes)

            df_chunk = df_chunk[f]
            df_chunk = df_chunk[["COMMUNE", "ARM", "IPONDI", "DCETUF"]]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/education.hdf" % context.cache_path, "movements")

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))):
        raise RuntimeError("RP MOBPRO data is not available")

    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("od_sco_path"))):
        raise RuntimeError("RP MOBSCO data is not available")

    return [
        os.path.getsize("%s/%s" % (context.config("data_path"), context.config("od_pro_path"))),
        os.path.getsize("%s/%s" % (context.config("data_path"), context.config("od_sco_path")))
    ]
