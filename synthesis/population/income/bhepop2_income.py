import numpy as np
import pandas as pd
from synthesis.population.income.uniform import _income_uniform_sample, MAXIMUM_INCOME_FACTOR
from bhepop2.tools import add_household_size_attribute, add_household_type_attribute
from bhepop2.sources.marginal_distributions import QuantitativeMarginalDistributions
from bhepop2.enrichment.bhepop2 import Bhepop2Enrichment

"""
This stage assigns a household income to each household of the synthesized
population, using the method Bhepop2 described in the package of the same name.
This method uses and fits the per-attribute distributions of Filosofi.
"""

INCOME_COLUMN = "income"


def configure(context):
    context.stage("data.income.municipality_attributes")
    context.stage("synthesis.population.sampled")
    context.stage("synthesis.population.spatial.home.zones")

    context.config("random_seed")


def _sample_income(context, args):
    commune_id, random_seed = args
    df_households, df_income = context.data("households"), context.data("income")

    random = np.random.RandomState(random_seed)

    # selection of commune population and distributions
    f = df_households["commune_id"] == commune_id
    df_selected = df_households[f]
    distribs = df_income[df_income["commune_id"] == commune_id]

    enrich_class = None
    try:
        source = QuantitativeMarginalDistributions(
            distribs,
            "Filosofi",
            attribute_selection=["size", "family_comp"],
            abs_minimum=0,
            relative_maximum=MAXIMUM_INCOME_FACTOR,
            delta_min=1000
        )

        enrich_class = Bhepop2Enrichment(df_selected, source, feature_name=INCOME_COLUMN, seed=random_seed)

    except AssertionError:
        pass

    if enrich_class is not None:
        try:
            pop = enrich_class.assign_feature_values()
            print("Enriched synpop on commune ", commune_id)
            # convert to monthly income
            pop[INCOME_COLUMN] = pop[INCOME_COLUMN] / 12
            pop[INCOME_COLUMN] = pop[INCOME_COLUMN].astype(int)
            incomes = pop[INCOME_COLUMN].values
            return f, incomes, "bhepop2"
        except Exception:
            print("Synpop enrichment on commune {} failed".format(commune_id))

    print("evaluate incomes on commune {} with original method".format(commune_id))

    # get global distribution of the commune
    distrib_all = distribs[distribs["modality"] == "all"]
    assert len(distrib_all) == 1
    centiles = list(distrib_all[["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]].iloc[0].values / 12)

    incomes = _income_uniform_sample(random, centiles, len(df_selected))

    return f, incomes, "eqasim"


def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    # Load data
    df_income = context.stage("data.income.municipality_attributes")
    df_population = context.stage("synthesis.population.sampled")

    df_population = add_household_size_attribute(df_population)
    df_population = add_household_type_attribute(df_population)

    df_households = df_population[[
        "household_id", "consumption_units", "size", "family_comp"
    ]].drop_duplicates("household_id")

    df_homes = context.stage("synthesis.population.spatial.home.zones")[[
        "household_id", "commune_id"
    ]]

    df_households = pd.merge(df_households, df_homes)

    # Perform sampling per commune
    with context.parallel(dict(households = df_households, income = df_income)) as parallel:
        commune_ids = df_households["commune_id"].unique()
        random_seeds = random.randint(10000, size = len(commune_ids))

        for f, incomes, method in context.progress(parallel.imap(_sample_income, zip(commune_ids, random_seeds)), label = "Imputing income ...", total = len(commune_ids)):
            df_households.loc[f, "household_income"] = incomes * df_households.loc[f, "consumption_units"]
            df_households.loc[f, "method"] = method

    # Cleanup
    df_households = df_households[["household_id", "household_income", "consumption_units"]]
    assert len(df_households) == len(df_households["household_id"].unique())

    return df_households
