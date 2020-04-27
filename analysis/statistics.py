import itertools
import numba

import numpy as np
import pandas as pd

@numba.jit(nopython = True, parallel = True)
def _combine_filter(filters):
    return np.logical_and.reduce(filters)

def marginalize(df, marginals, weight_column = "weight", count_column = "weight"):
    assert weight_column in df or weight_column is None
    assert not count_column in df or weight_column == count_column

    # Find unique columns that are involved to speed up process
    unique_columns = set()

    for marginal in marginals:
        unique_columns |= set(marginal)

    unique_columns = list(unique_columns)

    # Find values of all unique columns
    unique_values = {}

    for column in unique_columns:
        assert column in df
        unique_values[column] = df[column].unique()

    # Find filters for all values in all columns
    filters = {}

    for column in unique_columns:
        column_filters = []
        filters[column] = column_filters

        for value in unique_values[column]:
            column_filters.append((df[column] == value).values)

    # Set up numpy weights
    weights = np.ones((len(df),)) if weight_column is None else df[weight_column].values

    # Go through all marginals and create a table per marginals
    results = {}

    for columns in marginals:
        if len(columns) == 0: # Total is requested
            total = len(df) if weight_column is None else df[weight_column].sum()
            results[columns] = pd.DataFrame.from_records([["value", total]], columns = ["total", count_column])
        else:
            marginal_records = []
            value_index_lists = [np.arange(len(unique_values[column])) for column in columns]

            for value_indices in itertools.product(*value_index_lists):
                marginal_values = [unique_values[column][value_index] for column, value_index in zip(columns, value_indices)]
                marginal_filters = [filters[column][value_index] for column, value_index in zip(columns, value_indices)]
                f = np.logical_and.reduce(marginal_filters)

                if weight_column is None:
                    marginal_count = np.count_nonzero(f)
                else:
                    marginal_count = weights[f].sum()

                marginal_records.append(marginal_values + [marginal_count])

            marginal_records = pd.DataFrame.from_records(marginal_records, columns = list(columns) + [count_column])
            results[columns] = marginal_records

    return results

def collect_sample(dfs, sample_column = "sample"):
    assert len(dfs) > 0
    assert not sample_column in dfs[0]

    first_columns = list(dfs[0].columns)

    for index, df in enumerate(dfs):
        assert list(df.columns) == first_columns
        df[sample_column] = index

    return pd.concat(dfs)

def collect_marginalized_sample(realizations, sample_column = "sample"):
    assert len(realizations) > 0

    marginals = realizations[0].keys()
    marginal_columns = { marginal: list(realizations[0][marginal].columns) for marginal in marginals }

    # Check that all realizations have the same structure as the first
    for realization in realizations:
        assert len(marginals - realization.keys()) == 0

        for marginal in marginals:
            assert list(realization[marginal].columns) == marginal_columns[marginal]

    # Go through all marginals and collect the samples
    sample = {}

    for marginal in marginals:
        sample[marginal] = collect_sample([realization[marginal] for realization in realizations], sample_column)

    return sample

def bootstrap(df, samples, sample_size = 1, sample_column = "sample", count_column = "weight", random = None, random_seed = None, aggregator = "mean", metrics = None):
    assert sample_size > 0

    # Prepare and check columns
    columns = list(df.columns)

    assert sample_column in columns
    assert count_column in columns

    columns.remove(sample_column)
    columns.remove(count_column)

    # Check random number generator
    if random is None and random_seed is None:
        random = np.random.RandomState()
    elif random is None and not random_seed is None:
        random = np.random.RandomState(random_seed)
    elif not random is None and not random_seed is None:
        raise RuntimeError("Please either provide a random number generator OR a random seed")

    # Aggregate the samples

    df_result = []
    df = pd.pivot_table(df, index = sample_column, columns = columns, values = count_column)

    if sample_size == 1:
        indices = random.randint(len(df), size = samples)
        df_result = df.iloc[indices].reset_index(drop = True)
    else:
        for k in range(samples):
            indices = random.randint(len(df), size = (sample_size,))

            df_sample = df.iloc[indices].aggregate([aggregator]).reset_index(drop = True)
            df_sample.columns.names = df.columns.names

            df_result.append(df_sample)

        df_result = pd.concat(df_result)

    df_result = df_result.unstack()

    if metrics is None:
        metrics = dict(
            mean = "mean", std = "std",  median = "median",
            min = "min", max = "max",
            q10 = lambda x: x.quantile(0.1), q90 = lambda x: x.quantile(0.9),
            q5 = lambda x: x.quantile(0.05), q95 = lambda x: x.quantile(0.95),
        )

    df_result = df_result.groupby(columns).aggregate(**metrics).reset_index()
    return df_result

def bootstrap_sampled_marginals(marginals, samples, sample_size = 1, sample_column = "sample", count_column = "weight", random = None, random_seed = None, aggregator = "mean", metrics = None):
    # Go through all marginals and bootstap them
    sample = {}

    for marginal in marginals.keys():
        sample[marginal] = bootstrap(marginals[marginal], samples, sample_size, sample_column, count_column, random, random_seed, aggregator, metrics)

    return sample

if __name__ == "__main__":
    def create_sample(random_seed):
        random = np.random.RandomState(random_seed)

        index = np.arange(100)
        ages = random.randint(10, size = 100) * 10
        gender = random.randint(2, size = 100)

        df = pd.DataFrame.from_records(zip(index, ages, gender), columns = ["person", "age", "gender"])
        df["gender"] = df["gender"].map({ 0: "male", 1: "female" }).astype("category")
        df["weight"] = 1.0

        return df

    sample = [create_sample(R) for R in range(10)]

    marginals = [marginalize(df, [("age",), ("gender",), ("age", "gender"), tuple()]) for df in sample]
    marginals = collect_marginalized_sample(marginals)

    metrics = bootstrap_sampled_marginals(marginals, 100, sample_size = 1)
    print(metrics)
