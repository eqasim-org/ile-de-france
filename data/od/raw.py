from tqdm import tqdm
import pandas as pd
import numpy as np
import simpledbf
import os

"""
Loads raw OD data from French census data.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    # First, load work

    table = simpledbf.Dbf5("%s/rp_2015/FD_MOBPRO_2015.dbf" % context.config("data_path"))
    records = []

    with context.progress(label = "Reading work flows ...", total = 7943392) as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))
            f = df_chunk["REGION"] == "11"
            f |= df_chunk["REGLT"] == "11"
            df_chunk = df_chunk[f]
            df_chunk = df_chunk[["COMMUNE", "ARM", "TRANS", "IPONDI", "DCLT", "REGLT"]]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/work.hdf" % context.cache_path, "movements")

    # Second, load education

    table = simpledbf.Dbf5("%s/rp_2015/FD_MOBSCO_2015.dbf" % context.config("data_path"))
    records = []

    with context.progress(label = "Reading education flows ...", total = 4782736) as progress:
        for df_chunk in table.to_dataframe(chunksize = 10240):
            progress.update(len(df_chunk))
            f = df_chunk["REGION"] == "11"
            f |= df_chunk["REGETUD"] == "11"
            df_chunk = df_chunk[f]
            df_chunk = df_chunk[["COMMUNE", "ARM", "IPONDI", "DCETUF", "REGETUD"]]

            if len(df_chunk) > 0:
                records.append(df_chunk)

    pd.concat(records).to_hdf("%s/education.hdf" % context.cache_path, "movements")

def validate(context):
    if not os.path.exists("%s/rp_2015/FD_MOBPRO_2015.dbf" % context.config("data_path")):
        raise RuntimeError("RP MOBPRO data is not available")

    if not os.path.exists("%s/rp_2015/FD_MOBSCO_2015.dbf" % context.config("data_path")):
        raise RuntimeError("RP MOBSCO data is not available")

    return [
        os.path.getsize("%s/rp_2015/FD_MOBPRO_2015.dbf" % context.config("data_path")),
        os.path.getsize("%s/rp_2015/FD_MOBSCO_2015.dbf" % context.config("data_path"))
    ]
