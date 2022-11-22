import numpy as np
import pandas as pd
import os

"""
Loads the regional aggregated income distribution.
"""

def configure(context):
    context.config("data_path")
    context.config("income_reg_path", "filosofi_2015/FILO_DISP_REG.xls")
    context.config("income_year", 15)

def execute(context):
    df = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("income_reg_path")),
        sheet_name = "ENSEMBLE", skiprows = 5
    )

    values = df[df["CODGEO"] == 11][
        [
            i + str(context.config("income_year"))
            for i in ["D1", "D2", "D3", "D4", "Q2", "D6", "D7", "D8", "D9"]
        ]
    ].values[0]

    return values

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("income_reg_path"))):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("income_reg_path")))
