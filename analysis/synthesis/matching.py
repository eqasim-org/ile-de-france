import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

def configure(context):
    population_samples = context.config("analysis_populations")
    random_seeds = (np.arange(population_samples) * 1000 + 1000).astype(int)

    for index, random_seed in enumerate(random_seeds):
        context.stage("synthesis.population.matched", {
            "random_seed": int(random_seed),
            "sampling_rate": context.config("sampling_rate")
        }, alias = "seed_%d" % index)

def execute(context):
    population_samples = context.config("analysis_populations")

    aggregated = {}

    for index in range(population_samples):
        info = context.get_info("seed_%d" % index, "matched_counts")

        for key, value in info.items():
            if not key in aggregated:
                aggregated[key] = []

            aggregated[key].append(value)

    aggregated = { k: np.array(v) for k, v in aggregated.items() }

    return aggregated
