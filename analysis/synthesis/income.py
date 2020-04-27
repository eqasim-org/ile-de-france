import pandas as pd
import numpy as np
import geopandas as gpd

import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

ESTIMATION_SAMPLE_SIZE = 1000

def configure(context):
    acquisition_sample_size = context.config("acquisition_sample_size")
    bs.configure(context, "synthesis.population.income", acquisition_sample_size)

def execute(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    probabilities = np.linspace(0.0, 1.0, 20)
    quantiles = []

    with context.progress(label = "Processing commute data ...", total = acquisition_sample_size) as progress:
        for df_income in bs.get_stages(context, "synthesis.population.income", acquisition_sample_size):
            income = 12 * df_income["household_income"] / df_income["consumption_units"]
            quantiles.append([income.quantile(p) for p in probabilities])
            progress.update()

    random = np.random.RandomState(0)

    quantiles = np.array(quantiles)
    indices = np.random.randint(acquisition_sample_size, size = ESTIMATION_SAMPLE_SIZE)

    mean = np.mean(quantiles[indices,:], axis = 0)
    q5 = np.percentile(quantiles[indices,:], 5, axis = 0)
    q95 = np.percentile(quantiles[indices,:], 95, axis = 0)

    return pd.DataFrame(dict(mean = mean, q5 = q5, q95 = q95, cdf = probabilities))
