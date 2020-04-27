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
ESTIMATION_SAMPLES = 1000
ERROR_THRESHOLD = 0.01

MARGINAL_LEVEL = "person"
MARGINAL = ("age_class", "sex")
VALUES = (3, "male")

MAXIMUM_SAMPLE_SIZE = 40

SAMPLING_RATE_LABELS = {
    0.001: "0.1%",
    0.01: "1%",
    0.05: "5%"
}

SAMPLING_RATE_COLORS = {
    0.01: plotting.COLORSET[0],
    0.001: plotting.COLORSET[1],
    0.05: plotting.COLORSET[2]
}

def configure(context):
    context.stage("analysis.reference.census.sociodemographics")

    for sampling_rate in SAMPLING_RATES:
        bt.configure(context, "synthesis.population.sampled", ACQUISITION_SAMPLE_SIZE, dict(
            sampling_rate = sampling_rate
        ), alias = "sample_%f" % sampling_rate)

def execute(context):
    # Obtain reference data
    reference = context.stage("analysis.reference.census.sociodemographics")
    reference = reference[MARGINAL_LEVEL][MARGINAL]

    reference = reference[np.logical_and.reduce([
        reference[name] == value for name, value in zip(MARGINAL, VALUES)
    ])]["weight"].values[0]

    # Gather marginal information
    df_data = []

    for sampling_rate in SAMPLING_RATES:
        df_marginals = []

        for df_stage in bt.get_stages(context, "sample_%f" % sampling_rate, sample_size = ACQUISITION_SAMPLE_SIZE):
            marginals.prepare_classes(df_stage)
            df_stage = stats.marginalize(df_stage, [MARGINAL], weight_column = None)[MARGINAL]
            df_stage["sampling_rate"] = sampling_rate
            df_marginals.append(df_stage)

        df_marginals = stats.collect_sample(df_marginals)
        df_marginals = df_marginals[np.logical_and.reduce([
            df_marginals[name] == value for name, value in zip(MARGINAL, VALUES)
        ])]

        df_data.append(df_marginals)

    df_data = pd.concat(df_data)

    sample_sizes = np.arange(1, MAXIMUM_SAMPLE_SIZE + 1)
    df_figure = []

    for sampling_rate in SAMPLING_RATES:
        for sample_size in context.progress(sample_sizes, label = "Calculating sample sizes ..."):
            df_marginals = df_data[df_data["sampling_rate"] == sampling_rate]
            df_marginals = df_marginals.drop(columns = ["sampling_rate"])

            df_bootstrap = stats.bootstrap(df_marginals, ESTIMATION_SAMPLES, sample_size, metrics = {
                "mean": "mean",
                "q5": lambda x: x.quantile(0.05),
                "q95": lambda x: x.quantile(0.95),
                "precision": lambda x: np.mean(np.abs(x / sampling_rate - reference) / reference <= ERROR_THRESHOLD)
            })

            df_bootstrap["sample_size"] = sample_size
            df_bootstrap["sampling_rate"] = sampling_rate

            df_figure.append(df_bootstrap)

    df_figure = pd.concat(df_figure)

    # Plotting
    plotting.setup()
    plt.figure(figsize = plotting.SHORT_FIGSIZE)

    for index, sampling_rate in enumerate(SAMPLING_RATES):
        df_rate = df_figure[df_figure["sampling_rate"] == sampling_rate]
        plt.plot(df_rate["sample_size"], df_rate["precision"], label = SAMPLING_RATE_LABELS[sampling_rate], color = SAMPLING_RATE_COLORS[sampling_rate])

    plt.plot([0, MAXIMUM_SAMPLE_SIZE + 1], [0.9, 0.9], 'k:')

    plt.xlim([1, MAXIMUM_SAMPLE_SIZE])
    plt.ylim([0, 1.05])
    plt.xlabel("Number of seeds $K$")
    plt.ylabel(r"Error probability")

    plt.gca().xaxis.set_major_locator(tck.FixedLocator([1, 10, 20, 30, 40]))
    plt.gca().yaxis.set_major_formatter(tck.FuncFormatter(lambda x, p: "%d%%" % (x * 100,)))

    plt.grid()
    plt.gca().set_axisbelow(True)

    plt.legend(loc = "best", title = "Sampling rate $s$")

    plt.tight_layout()
    plt.savefig("%s/error_probability.pdf" % context.path())
    plt.close()
