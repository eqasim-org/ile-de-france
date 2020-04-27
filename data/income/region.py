import numpy as np
import pandas as pd
import os

"""
Loads the regional aggregated income distribution.
"""

def configure(context):
    context.config("data_path")

def execute(context):
    df = pd.read_excel(
        "%s/filosofi_2015/FILO_DISP_REG.xls" % context.config("data_path"),
        sheet_name = "ENSEMBLE", skiprows = 5
    )

    values = df[df["CODGEO"] == 11][[
        "D115", "D215", "D315", "D415", "Q215", "D615", "D715", "D815", "D915"
    ]].values[0]

    return values

def validate(context):
    if not os.path.exists("%s/filosofi_2015/FILO_DISP_REG.xls" % context.config("data_path")):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/filosofi_2015/FILO_DISP_REG.xls" % context.config("data_path"))
