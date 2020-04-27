import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import documentation.plotting as plotting

import analysis.bootstrapping as bt
import analysis.marginals as marginals
import analysis.statistics as stats

SAMPLING_RATE = 0.01
ACQUISITION_SAMPLE_SIZE = 200
ESTIMATION_SAMPLES = 1000

MARGINAL_LEVEL = "person"
MARGINAL = ("age_class", "sex")
VALUES = (3, "male")

MAXIMUM_SAMPLE_SIZE = 20

def configure(context):
    context.stage("analysis.reference.census.sociodemographics")

    bt.configure(context, "synthesis.population.sampled", ACQUISITION_SAMPLE_SIZE, dict(
        sampling_rate = SAMPLING_RATE
    ), alias = "sample")

def execute(context):
    # Obtain reference data
    reference = context.stage("analysis.reference.census.sociodemographics")
    reference = reference[MARGINAL_LEVEL][MARGINAL]

    reference = reference[np.logical_and.reduce([
        reference[name] == value for name, value in zip(MARGINAL, VALUES)
    ])]["weight"].values[0]

    # Gather information
    df_marginals = []

    for df_stage in bt.get_stages(context, "sample", sample_size = ACQUISITION_SAMPLE_SIZE):
        marginals.prepare_classes(df_stage)
        df_marginals.append(stats.marginalize(df_stage, [MARGINAL], weight_column = None)[MARGINAL])

    df_marginals = stats.collect_sample(df_marginals)
    df_marginals = df_marginals[np.logical_and.reduce([
        df_marginals[name] == value for name, value in zip(MARGINAL, VALUES)
    ])]

    sample_sizes = np.arange(1, MAXIMUM_SAMPLE_SIZE + 1)
    df_figure = []

    for sample_size in context.progress(sample_sizes, label = "Calculating sample sizes ..."):
        df_bootstrap = stats.bootstrap(df_marginals, ESTIMATION_SAMPLES, sample_size)
        df_bootstrap["sample_size"] = sample_size
        df_figure.append(df_bootstrap)

    df_figure = pd.concat(df_figure)

    df_figure["mean"] /= SAMPLING_RATE
    df_figure["q5"] /= SAMPLING_RATE
    df_figure["q95"] /= SAMPLING_RATE

    # Prepare plot
    plotting.setup()
    plt.figure(figsize = plotting.SHORT_FIGSIZE)

    plt.fill_between(df_figure["sample_size"], df_figure["q5"], df_figure["q95"], alpha = 0.25, label = "90% Conf.", color = plotting.COLORSET[0], linewidth = 0.0)
    plt.plot([1, MAXIMUM_SAMPLE_SIZE], [reference] * 2, 'k--', label = "Ref. $w$")
    plt.plot([1, MAXIMUM_SAMPLE_SIZE], [reference * 0.99] * 2, 'k:', label = "1% Err.")
    plt.plot([1, MAXIMUM_SAMPLE_SIZE], [reference * 1.01] * 2, 'k:')
    plt.plot(df_figure["sample_size"], df_figure["mean"], label = r"$\mathrm{\mathbf{E}}[\tilde w_K]$", color = plotting.COLORSET[0])

    plt.xlim([1, MAXIMUM_SAMPLE_SIZE])
    plt.xlabel("Number of seeds $K$")
    plt.ylabel("Stratum weight")

    plt.gca().xaxis.set_major_locator(tck.FixedLocator([1, 5, 10, 15, 20, 25]))
    plt.gca().yaxis.set_major_formatter(tck.FuncFormatter(lambda x, p: "%.2fM" % (x * 1e-6,)))

    plt.grid()
    plt.gca().set_axisbelow(True)

    plt.legend(loc = "best", ncol = 2)

    plt.tight_layout()
    plt.savefig("%s/sample_count.pdf" % context.path())
    plt.close()
