
#
# --%%  pkmath.py    %%--
#

__version__ = "1.0"

import logging

logger = logging.getLogger(__name__)


#
# -%  MATH: Normalize column(s) of data in Pandas  %-

def scaler_absolute_maximum(series):
    """Maximum absolute scaling method rescales each feature to be a value between -1 and 1.
    
    Inspired by:
        https://datagy.io/pandas-normalize-column/
    """
    import pandas as pd
    return series / series.abs().max()

def scaler_min_max(series):
    """Min-max feature scaling (normalization) rescales the dataset feature to a range of 0 - 1.

    Inspired by:
        https://datagy.io/pandas-normalize-column/
    """
    import pandas as pd
    return (series - series.min()) / (series.max() - series.min())

def scaler_z_scores(series):
    """Transforms the data into z-scores (standardization). Data becomes a distribution of values
    with mean 0 and standard deviation 1.

    Inspired by:
        https://datagy.io/pandas-normalize-column/
    """
    import pandas as pd
    return (series - series.mean()) / series.std()



#
# -%  MATH: Rank-based inverse normal transformation  %-

def rank_int(series, c=3.0/8, stochastic=True):
    """Perform rank-based inverse normal transformation on pandas series.

    If stochastic is True ties are given rank randomly, otherwise ties will share the same value.
    NaN values are ignored.
    Args:
        param1 (pandas.Series):   Series of values to transform
        param2 (Optional[float]): Constand parameter (Bloms constant)
        param3 (Optional[bool]):  Whether to randomise rank of ties
    Returns:
        pandas.Series
    Inspired by:
        https://www.well.ox.ac.uk/~gav/qctool_v2/documentation/sample_file_formats.html
    """
    import pandas as pd
    import numpy as np
    import scipy.stats as ss
    def rank_to_normal(rank, c, n):
        x = (rank - c) / (n - 2*c + 1) # Standard quantile function
        return ss.norm.ppf(x)

    # Check input
    assert isinstance(series, pd.Series)
    assert isinstance(c, float)

    np.random.seed(123) # Set seed
    orig_idx = series.index # Take original series indexes
    series = series.loc[~pd.isnull(series)] # Drop NaNs
    if stochastic:
        series = series.loc[np.random.permutation(series.index)] # Shuffle by index
        rank = ss.rankdata(series, method="ordinal") # Get rank, ties are determined by their position in the series (hence why we randomised the series)
    else:
        rank = ss.rankdata(series, method="average") # Get rank, ties are averaged
    rank = pd.Series(rank, index=series.index) # Convert numpy array back to series
    transformed = rank.apply(rank_to_normal, c=c, n=len(rank)) # Convert rank to normal distribution
    return transformed[orig_idx]


