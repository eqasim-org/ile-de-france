import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import documentation.plotting as plotting

import analysis.bootstrapping as bt
import analysis.marginals as marginals
import analysis.statistics as stats

SAMPLING_RATES = [0.001, 0.01, 0.05]
ACQUISITION_SAMPLE_SIZE = 200
ESTIMATION_SAMPLE_SIZE = 1000
ERROR_THRESHOLD = 0.01

MAXIMUM_SAMPLE_SIZE = 40

MARGINALS = [
    ("age_class",), ("sex",), ("employed",), ("studies",),
    ("socioprofessional_class",)
]

def configure(context):
    context.stage("analysis.reference.census.sociodemographics")

    for sampling_rate in SAMPLING_RATES:
        bt.configure(context, "synthesis.population.sampled", ACQUISITION_SAMPLE_SIZE, dict(
            sampling_rate = sampling_rate
        ), alias = "sample_%f" % sampling_rate)

def parallel_bootstrap(context, task):
    df_marginal, df_reference, sampling_rate, sample_size, marginal = task

    df_bootstrap = stats.bootstrap(
        df_marginal, ESTIMATION_SAMPLE_SIZE, sample_size, metrics = {
            "confidence": lambda x: (np.abs(x / sampling_rate) / df_reference[df_reference[marginal[0]] == x.index.values[0][0]]["reference"].values[0] - 1 <= ERROR_THRESHOLD).mean()
        }
    )

    df_bootstrap = df_bootstrap.rename(columns = { marginal[0]: "value" })
    df_bootstrap["marginal"] = marginal[0]
    df_bootstrap["sampling_rate"] = sampling_rate
    df_bootstrap["sample_size"] = sample_size

    context.progress.update()
    return df_bootstrap

def execute(context):
    # Obtain reference data
    reference_marginals = context.stage("analysis.reference.census.sociodemographics")["person"]

    # Gather information
    df_data = []
    total = len(SAMPLING_RATES) * len(MARGINALS) * MAXIMUM_SAMPLE_SIZE

    with context.progress(total = total, label = "Sampling analysis ...") as progress:
        for sampling_rate in SAMPLING_RATES:
            rate_marginals = []

            for df_stage in bt.get_stages(context, "sample_%f" % sampling_rate, sample_size = ACQUISITION_SAMPLE_SIZE):
                marginals.prepare_classes(df_stage)
                rate_marginals.append(stats.marginalize(df_stage, MARGINALS, weight_column = None))

            rate_marginals = stats.collect_marginalized_sample(rate_marginals)
            tasks = []

            for marginal in MARGINALS:
                df_marginal = rate_marginals[marginal].copy()
                df_reference = reference_marginals[marginal].rename(columns = { "weight": "reference" })

                for sample_size in range(1, MAXIMUM_SAMPLE_SIZE + 1):
                    tasks.append((df_marginal, df_reference, sampling_rate, sample_size, marginal))

            with context.parallel() as parallel:
                df_sampling_rate = pd.concat(parallel.imap_unordered(parallel_bootstrap, tasks))
                df_data.append(df_sampling_rate)

    df_data = pd.concat(df_data)
    return df_data
