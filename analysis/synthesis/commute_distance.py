import pandas as pd
import numpy as np
import geopandas as gpd

import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

ESTIMATION_SAMPLE_SIZE = 1000

def configure(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    bs.configure(context, "synthesis.population.spatial.home.locations", acquisition_sample_size)
    bs.configure(context, "synthesis.population.spatial.primary.locations", acquisition_sample_size)
    bs.configure(context, "synthesis.population.sampled", acquisition_sample_size)

def execute(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    feeder = zip(
        bs.get_stages(context, "synthesis.population.spatial.home.locations", acquisition_sample_size),
        bs.get_stages(context, "synthesis.population.spatial.primary.locations", acquisition_sample_size),
        bs.get_stages(context, "synthesis.population.sampled", acquisition_sample_size),
    )

    probabilities = np.linspace(0.0, 1.0, 20)
    quantiles = { "work": [], "education": [] }

    with context.progress(label = "Processing commute data ...", total = acquisition_sample_size) as progress:
        for df_home, df_spatial, df_persons in feeder:
            # Prepare home
            df_home = pd.merge(df_home, df_persons[["person_id", "household_id"]], on = "household_id")
            df_home = df_home[["person_id", "geometry"]].set_index("person_id").sort_index()
            assert len(df_home) == len(df_persons)

            for index, name in enumerate(("work", "education")):
                df_destination = df_spatial[index]
                df_destination = df_destination[["person_id", "geometry"]]
                df_destination = df_destination.set_index("person_id").sort_index()

                df_compare = df_home.loc[df_destination.index]
                assert len(df_destination) == len(df_compare)

                distances = df_destination["geometry"].distance(df_compare["geometry"]) * 1e-3

                quantiles[name].append([
                    distances.quantile(p)
                    for p in probabilities
                ])

            progress.update()

    result = {}
    random = np.random.RandomState(0)

    for name in ("work", "education"):
        data = np.array(quantiles[name])
        indices = np.random.randint(acquisition_sample_size, size = ESTIMATION_SAMPLE_SIZE)

        mean = np.mean(data[indices,:], axis = 0)
        q5 = np.percentile(data[indices,:], 5, axis = 0)
        q95 = np.percentile(data[indices,:], 95, axis = 0)

        df = pd.DataFrame(dict(mean = mean, q5 = q5, q95 = q95, cdf = probabilities))
        result[name] = df

    return result
