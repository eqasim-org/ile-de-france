import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import documentation.plotting as plotting

SAMPLING_RATE = 0.05
POPULATION_SAMPLES = 200
ESTIMATION_SAMPLES = 1000

def configure(context):
    context.stage("analysis.matching", {
        "sampling_rate": SAMPLING_RATE,
        "analysis_populations": POPULATION_SAMPLES,
    }, alias = "data")

def execute(context):
    data = context.stage("data")
    variables = max(data.keys()) + 1

    indices = np.random.randint(0, len(data[0]), size = ESTIMATION_SAMPLES)

    means = [np.mean(data[v][indices] / data[0][indices]) for v in range(variables)]
    q10s = [np.percentile(data[v][indices] / data[0][indices], 10) for v in range(variables)]
    q90s = [np.percentile(data[v][indices] / data[0][indices], 90) for v in range(variables)]

    # Prepare plot
    plotting.setup()

    plt.figure()
    plt.bar(range(variables), means, color = plotting.COLORS["synthetic"])

    for v, q10, q90 in zip(range(variables), q10s, q90s):
        plt.plot([v, v,], [q10, q90], linewidth = 1, label = "90% Conf.", color = "k")

    plt.xlabel("Variables")
    plt.ylabel("Matching rate")

    plt.gca().yaxis.set_major_locator(tck.FixedLocator(np.arange(100) * 0.2))
    plt.gca().yaxis.set_major_formatter(tck.FuncFormatter(lambda x,p: "%d%%" % (100 * x,)))

    plt.tight_layout()
    plt.savefig("%s/matching_rate.pdf" % context.path())
