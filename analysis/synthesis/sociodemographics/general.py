import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

ESTIMATION_SAMPLE_SIZE = 1000

def configure(context):
    acquisition_sample_size = context.config("acquisition_sample_size")
    bs.configure(context, "synthesis.population.enriched", acquisition_sample_size)

def execute(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    person_marginals = []
    household_marginals = []

    for df in bs.get_stages(context, "synthesis.population.enriched", acquisition_sample_size):
        marginals.prepare_classes(df)

        person_marginals.append(stats.marginalize(df, marginals.ANALYSIS_PERSON_MARGINALS, weight_column = None))
        household_marginals.append(stats.marginalize(df.drop_duplicates("household_id"), marginals.ANALYSIS_HOUSEHOLD_MARGINALS, weight_column = None))

    person_marginals = stats.collect_marginalized_sample(person_marginals)
    household_marginals = stats.collect_marginalized_sample(household_marginals)

    person_marginals = stats.bootstrap_sampled_marginals(person_marginals, ESTIMATION_SAMPLE_SIZE)
    household_marginals = stats.bootstrap_sampled_marginals(household_marginals, ESTIMATION_SAMPLE_SIZE)

    return dict(person = person_marginals, household = household_marginals)
