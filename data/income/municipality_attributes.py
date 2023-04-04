import os
from bhepop2.tools import read_filosofi


def configure(context):
    context.config("data_path")
    context.stage("data.spatial.municipalities")


def execute(context):

    distributions = read_filosofi("%s/filosofi_2015/FILO_DISP_COM.xls" %
                                  context.config("data_path"))
    distributions.rename(
        columns={
            "q1": "D1",
            "q2": "D2",
            "q3": "D3",
            "q4": "D4",
            "q5": "D5",
            "q6": "D6",
            "q7": "D7",
            "q8": "D8",
            "q9": "D9",
        },
        inplace=True,
    )
    return distributions


def validate(context):
    if not os.path.exists("%s/filosofi_2015/FILO_DISP_COM.xls" % context.config("data_path")):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/filosofi_2015/FILO_DISP_COM.xls" % context.config("data_path"))
