import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import documentation.plotting as plotting

import numpy as np

def configure(context):
    context.stage("analysis.matsim.mode_share")
    context.stage("analysis.reference.hts.mode_share")

DISTANCE_CLASSES = np.arange(1, 41) * 500

labels = {
    "car": "Car driver",
    "pt": "Public transport",
    "bike": "Bicycle",
    "walk": "Walking",
    "car_passenger": "Car passenger"
}

def execute(context):
    plotting.setup()
    plt.figure(figsize = plotting.WIDE_FIGSIZE)

    df = context.stage("analysis.matsim.mode_share")
    df_reference = context.stage("analysis.reference.hts.mode_share")

    for index, mode in enumerate(["car", "pt", "bike", "walk", "car_passenger"]):
        df_mode = df[df["mode"] == mode]

        mean = df_mode[df_mode["metric"] == "mean"]["share"].values[:-1]
        q10 = df_mode[df_mode["metric"] == "q10"]["share"].values[:-1]
        q90 = df_mode[df_mode["metric"] == "q90"]["share"].values[:-1]

        plt.fill_between(DISTANCE_CLASSES * 1e-3, q10 * 1e2, q90 * 1e2, color = plotting.COLORSET5[index], linewidth = 0.0, alpha = 0.3)
        plt.plot(DISTANCE_CLASSES * 1e-3, mean * 1e2, color = plotting.COLORSET5[index], linewidth = 1.0, label = labels[mode])

        df_mode = df_reference[df_reference["mode"] == mode]
        plt.plot(DISTANCE_CLASSES * 1e-3, df_mode["share"].values[:-1] * 1e2, color = plotting.COLORSET5[index], linewidth = 1.0, linestyle = ":")

    plt.grid()
    plt.xlabel("Euclidean distance [km]")
    plt.ylabel("Trip-based mode share [%]")
    plt.legend(loc = "best", ncol = 3)

    plt.xlim([0.5, 20])

    plt.tight_layout()
    plt.savefig("%s/mode_share.pdf" % context.path())
    plt.close()
