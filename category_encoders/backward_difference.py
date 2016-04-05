"""

.. module:: backward_difference
  :synopsis:
  :platform:

"""

import copy
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from patsy.highlevel import dmatrix
from category_encoders.ordinal import OrdinalEncoder

__author__ = 'willmcginnis'


def backward_difference_coding(X_in, cols=None):
    """

    :param X:
    :return:
    """

    X = copy.deepcopy(X_in)

    if cols is None:
        cols = X.columns.values
        pass_thru = []
    else:
        pass_thru = [col for col in X.columns.values if col not in cols]

    bin_cols = []
    for col in cols:
        mod = dmatrix("C(%s, Diff)" % (col, ), X)
        for dig in range(len(mod[0])):
            X[col + '_%d' % (dig, )] = mod[:, dig]
            bin_cols.append(col + '_%d' % (dig, ))

    X = X.reindex(columns=bin_cols + pass_thru)
    X.fillna(0.0)
    return X


class BackwardDifferenceEncoder(BaseEstimator, TransformerMixin):
    """

    """
    def __init__(self, verbose=0, cols=None):
        """

        :param verbose:
        :param cols:
        :return:
        """

        self.verbose = verbose
        self.cols = cols
        self.ordinal_encoder = OrdinalEncoder(verbose=verbose, cols=cols)

    def fit(self, X, y=None, **kwargs):
        """

        :param X:
        :param y:
        :param kwargs:
        :return:
        """

        self.ordinal_encoder = self.ordinal_encoder.fit(X)

        return self

    def transform(self, X):
        """

        :param X:
        :return:
        """

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        X = self.ordinal_encoder.transform(X)

        return backward_difference_coding(X, cols=self.cols)