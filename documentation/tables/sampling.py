import numpy as np
import pandas as pd

import analysis.synthesis.sampling as sampling
import analysis.marginals

CONFIDENCE_THRESHOLD = 0.90

def configure(context):
    context.stage("analysis.synthesis.sampling")

def find_minimum_sample_size(x):
    return np.argmax(x["confidence"].values > CONFIDENCE_THRESHOLD) + 1 if np.any(x["confidence"].values > CONFIDENCE_THRESHOLD) else len(x)

def label(row):
    if row["marginal"] == "age_class":
        return analysis.marginals.AGE_CLASS_LABELS[row["value"]]

    elif row["marginal"] == "sex":
        return row["value"].capitalize()

    elif row["marginal"] == "employed":
        return "Employed" if row["value"] else "Unemployed"

    elif row["marginal"] == "studies":
        return "Yes" if row["value"] else "No"

    elif row["marginal"] == "socioprofessional_class":
        return analysis.marginals.SOCIOPROFESIONAL_CLASS_LABELS[row["value"]]

def execute(context):
    df_sampling = context.stage("analysis.synthesis.sampling").sort_values(by = [
        "marginal", "value", "sampling_rate", "sample_size"
    ])

    df_sampling = df_sampling.groupby(["marginal", "value", "sampling_rate"]).apply(find_minimum_sample_size).reset_index(name = "minimum_sample_size")
    df_sampling = pd.pivot_table(df_sampling, index = ["marginal", "value"], columns = "sampling_rate", values = "minimum_sample_size")

    df_sampling = df_sampling.reset_index()

    df_sampling["value"] = df_sampling.apply(label, axis = 1, raw = False)

    df_sampling["marginal"] = df_sampling["marginal"].map({
        "age_class": "Age",
        "sex": "Sex",
        "employed": "Employed",
        "studies": "Studies",
        "socioprofessional_class": "Socioprof. Cat."
    })

    df_sampling.columns = ["Variable", "Stratum"] + [str(s) for s in sampling.SAMPLING_RATES]
    df_sampling = df_sampling.set_index(["Variable", "Stratum"])
    df_sampling.columns = pd.MultiIndex.from_tuples([("Sampling rate $s$", str(s)) for s in sampling.SAMPLING_RATES])

    df_sampling.to_latex("%s/sampling_table.tex" % context.path(), escape = False)
