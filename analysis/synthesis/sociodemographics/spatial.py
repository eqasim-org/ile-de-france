import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

import pandas as pd

ESTIMATION_SAMPLE_SIZE = 1000

def configure(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    bs.configure(context, "synthesis.population.enriched", acquisition_sample_size)
    bs.configure(context, "synthesis.population.spatial.home.zones", acquisition_sample_size)

def execute(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    person_marginals = []
    household_marginals = []

    feeder = zip(
        bs.get_stages(context, "synthesis.population.enriched", acquisition_sample_size),
        bs.get_stages(context, "synthesis.population.spatial.home.zones", acquisition_sample_size)
    )

    for df, df_home in feeder:
        df = pd.merge(df, df_home[["household_id", "departement_id", "commune_id"]])
        marginals.prepare_classes(df)

        person_marginals.append(stats.marginalize(df, marginals.SPATIAL_PERSON_MARGINALS, weight_column = None))
        household_marginals.append(stats.marginalize(df.drop_duplicates("household_id"), marginals.SPATIAL_HOUSEHOLD_MARGINALS, weight_column = None))

    person_marginals = stats.collect_marginalized_sample(person_marginals)
    household_marginals = stats.collect_marginalized_sample(household_marginals)

    person_marginals = stats.bootstrap_sampled_marginals(person_marginals, ESTIMATION_SAMPLE_SIZE)
    household_marginals = stats.bootstrap_sampled_marginals(household_marginals, ESTIMATION_SAMPLE_SIZE)

    return dict(person = person_marginals, household = household_marginals)
