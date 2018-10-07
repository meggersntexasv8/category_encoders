import doctest
import os
from datetime import timedelta

import numpy as np
import pandas as pd
import sklearn
import category_encoders.tests.test_utils as tu
from sklearn.utils.estimator_checks import check_transformer_general, check_transformers_unfitted
from unittest2 import TestSuite, TextTestRunner, TestCase  # or `from unittest import ...` if on Python 3.4+

import category_encoders as encoders

__author__ = 'willmcginnis'


def verify_inverse_transform(x, x_inv):
    """
    Verify x is equal to x_inv. The test returns true for NaN.equals(NaN) as it should.

    """
    assert x.equals(x_inv)

# data definitions
np_X = tu.create_array(n_rows=100)
np_X_t = tu.create_array(n_rows=50, extras=True)
np_y = np.random.randn(np_X.shape[0]) > 0.5
np_y_t = np.random.randn(np_X_t.shape[0]) > 0.5
X = tu.create_dataset(n_rows=100)
X_t = tu.create_dataset(n_rows=50, extras=True)
y = pd.DataFrame(np_y)
y_t = pd.DataFrame(np_y_t)

# this class utilises parametrised tests where we loop over different encoders
# tests that are applicable to only one encoder are the end of the class
class TestEncoders(TestCase):

    def test_np(self):
        for encoder_name in encoders.__all__:
            with self.subTest(encoder_name=encoder_name):

                # Encode a numpy array
                enc = getattr(encoders, encoder_name)()
                enc.fit(np_X, np_y)
                tu.verify_numeric(enc.transform(np_X_t))

    def test_classification(self):
        for encoder_name in encoders.__all__:
            with self.subTest(encoder_name=encoder_name):
                cols = ['unique_str', 'underscore', 'extra', 'none', 'invariant', 321]

                enc = getattr(encoders, encoder_name)(cols=cols)
                enc.fit(X, np_y)
                tu.verify_numeric(enc.transform(X_t))

                enc = getattr(encoders, encoder_name)(verbose=1)
                enc.fit(X, np_y)
                tu.verify_numeric(enc.transform(X_t))

                enc = getattr(encoders, encoder_name)(drop_invariant=True)
                enc.fit(X, np_y)
                tu.verify_numeric(enc.transform(X_t))

                enc = getattr(encoders, encoder_name)(return_df=False)
                enc.fit(X, np_y)
                self.assertTrue(isinstance(enc.transform(X_t), np.ndarray))
                self.assertEqual(enc.transform(X_t).shape[0], X_t.shape[0], 'Row count must not change')

                # documented in issue #122
                # when we use the same encoder on two different datasets, it should not explode
                # X_a = pd.DataFrame(data=['1', '2', '2', '2', '2', '2'], columns=['col_a'])
                # X_b = pd.DataFrame(data=['1', '1', '1', '2', '2', '2'], columns=['col_b']) # different values and name
                # y_dummy = [True, False, True, False, True, False]
                # enc = getattr(encoders, encoder_name)()
                # enc.fit(X_a, y_dummy)
                # enc.fit(X_b, y_dummy)
                # verify_numeric(enc.transform(X_b))

    def test_impact_encoders(self):
        for encoder_name in ['LeaveOneOutEncoder', 'TargetEncoder', 'WOEEncoder']:
            with self.subTest(encoder_name=encoder_name):

                # encode a numpy array and transform with the help of the target
                enc = getattr(encoders, encoder_name)()
                enc.fit(np_X, np_y)
                tu.verify_numeric(enc.transform(np_X_t, np_y_t))

                # target is a DataFrame
                enc = getattr(encoders, encoder_name)()
                enc.fit(X, y)
                tu.verify_numeric(enc.transform(X_t, y_t))

                # when we run transform(X, y) and there is a new value in X, something is wrong and we raise an error
                enc = getattr(encoders, encoder_name)(impute_missing=True, handle_unknown='error', cols=['extra'])
                enc.fit(X, y)
                self.assertRaises(ValueError, enc.transform, (X_t, y_t))

    def test_error_handling(self):
        for encoder_name in encoders.__all__:
            with self.subTest(encoder_name=encoder_name):

                # we exclude some columns
                X = tu.create_dataset(n_rows=100)
                X = X.drop(['unique_str', 'none'], axis=1)
                X_t = tu.create_dataset(n_rows=50, extras=True)
                X_t = X_t.drop(['unique_str', 'none'], axis=1)

                # illegal state, we have to first train the encoder...
                enc = getattr(encoders, encoder_name)()
                with self.assertRaises(ValueError):
                    enc.transform(X)

                # wrong count of attributes
                enc = getattr(encoders, encoder_name)()
                enc.fit(X, y)
                with self.assertRaises(ValueError):
                    enc.transform(X_t.iloc[:, 0:3])

                # no cols
                enc = getattr(encoders, encoder_name)(cols=[])
                enc.fit(X, y)
                self.assertTrue(enc.transform(X_t).equals(X_t))

    def test_handle_unknown_error(self):
        # BaseN has problems with None -> ignore None
        X = tu.create_dataset(n_rows=100, has_none=False)
        X_t = tu.create_dataset(n_rows=50, extras=True, has_none=False)

        for encoder_name in (set(encoders.__all__) - {'HashingEncoder'}):  # HashingEncoder supports new values by design -> excluded
            with self.subTest(encoder_name=encoder_name):

                # new value during scoring
                enc = getattr(encoders, encoder_name)(handle_unknown='error')
                enc.fit(X, y)
                with self.assertRaises(ValueError):
                    _ = enc.transform(X_t)

    def test_sklearn_compliance(self):
        for encoder_name in encoders.__all__:
            with self.subTest(encoder_name=encoder_name):

                # in sklearn < 0.19.0, these methods require classes,
                # in sklearn >= 0.19.0, these methods require instances
                if sklearn.__version__ < '0.19.0':
                    encoder = getattr(encoders, encoder_name)
                else:
                    encoder = getattr(encoders, encoder_name)()

                check_transformer_general(encoder_name, encoder)
                check_transformers_unfitted(encoder_name, encoder)

    def test_inverse_transform(self):
        # we do not allow None in these data (but "none" column without any None is ok)
        X = tu.create_dataset(n_rows=100, has_none=False)
        X_t = tu.create_dataset(n_rows=50, has_none=False)
        X_t_extra = tu.create_dataset(n_rows=50, extras=True, has_none=False)
        cols = ['underscore', 'none', 'extra', 321]

        for encoder_name in ['BaseNEncoder', 'BinaryEncoder', 'OneHotEncoder', 'OrdinalEncoder']:
            with self.subTest(encoder_name=encoder_name):

                # simple run
                enc = getattr(encoders, encoder_name)(verbose=1, cols=cols)
                enc.fit(X)
                verify_inverse_transform(X_t, enc.inverse_transform(enc.transform(X_t)))

                # when a new value is encountered, do not raise an exception
                enc = getattr(encoders, encoder_name)(verbose=1, cols=cols)
                enc.fit(X, y)
                _ = enc.inverse_transform(enc.transform(X_t_extra))

    def test_types(self):

        X = pd.DataFrame({
            'Int': [1, 2, 1, 2],
            'Float': [1.1, 2.2, 3.3, 4.4],
            'Complex': [3.45J, 3.45J, 3.45J, 3.45J],
            'None': [None, None, None, None],
            'Str': ['a', 'c', 'c', 'd'],
            'PdTimestamp': [pd.Timestamp('2012-05-01'), pd.Timestamp('2012-05-02'), pd.Timestamp('2012-05-03'), pd.Timestamp('2012-05-06')],
            'PdTimedelta': [pd.Timedelta('1 days'), pd.Timedelta('2 days'), pd.Timedelta('1 days'), pd.Timedelta('1 days')],
            'TimeDelta': [timedelta(-9999), timedelta(-9), timedelta(-1), timedelta(999)],
            'Bool': [False, True, True, False],
            'Tuple': [('a', 'tuple'), ('a', 'tuple'), ('a', 'tuple'), ('b', 'tuple')],
            # 'Categorical': pd.Categorical(list('bbea'), categories=['e', 'a', 'b'], ordered=True),
            # 'List': [[1,2], [2,3], [3,4], [4,5]],
            # 'Dictionary': [{1: "a", 2: "b"}, {1: "a", 2: "b"}, {1: "a", 2: "b"}, {1: "a", 2: "b"}],
            # 'Set': [{'John', 'Jane'}, {'John', 'Jane'}, {'John', 'Jane'}, {'John', 'Jane'}],
            # 'Array': [array('i'), array('i'), array('i'), array('i')]
        })
        y = [1, 0, 0, 1]

        for encoder_name in encoders.__all__:
            encoder = getattr(encoders, encoder_name)()
            encoder.fit_transform(X, y)

    def test_preserve_column_order(self):
        binary_cat_example = pd.DataFrame(
            {'Trend': ['UP', 'UP', 'DOWN', 'FLAT', 'DOWN', 'UP', 'DOWN', 'FLAT', 'FLAT', 'FLAT'],
             'target': [1, 1, 0, 0, 1, 0, 0, 0, 1, 1]}, columns=['Trend', 'target'])

        for encoder_name in encoders.__all__:
            with self.subTest(encoder_name=encoder_name):
                print(encoder_name)
                encoder = getattr(encoders, encoder_name)()
                result = encoder.fit_transform(binary_cat_example, binary_cat_example['target'])
                columns = result.columns.values

                self.assertTrue('target' in columns[-1], "Target must be the last column as in the input")

    def test_tmp_column_name(self):
        binary_cat_example = pd.DataFrame(
            {'Trend': ['UP', 'UP', 'DOWN', 'FLAT'],
             'Trend_tmp': ['UP', 'UP', 'DOWN', 'FLAT'],
             'target': [1, 1, 0, 0]}, columns=['Trend', 'Trend_tmp', 'target'])

        for encoder_name in ['LeaveOneOutEncoder', 'TargetEncoder', 'WOEEncoder']:
            with self.subTest(encoder_name=encoder_name):
                encoder = getattr(encoders, encoder_name)()
                _ = encoder.fit_transform(binary_cat_example, binary_cat_example['target'])

    def test_unique_column_is_not_predictive(self):
        for encoder_name in ['LeaveOneOutEncoder', 'TargetEncoder', 'WOEEncoder']:
            with self.subTest(encoder_name=encoder_name):
                encoder = getattr(encoders, encoder_name)()
                result = encoder.fit_transform(X[['unique_str']], y)
                self.assertTrue(all(result.var() < 0.001), 'The unique string column must not be predictive of the label')

    def test_leave_one_out(self):
        enc = encoders.LeaveOneOutEncoder(verbose=1, randomized=True, sigma=0.1)
        enc.fit(X, y)
        tu.verify_numeric(enc.transform(X_t))
        tu.verify_numeric(enc.transform(X_t, y_t))

    def test_leave_one_out_values(self):
        df = pd.DataFrame({
            'color': ["a", "a", "a", "b", "b", "b"],
            'outcome': [1, 0, 0, 1, 0, 1]})

        X = df.drop('outcome', axis=1)
        y = df.drop('color', axis=1)

        ce_leave = encoders.LeaveOneOutEncoder(cols=['color'], randomized=False)
        obtained = ce_leave.fit_transform(X, y['outcome'])

        self.assertEquals([0.0, 0.5, 0.5, 0.5, 1.0, 0.5], list(obtained['color']))

    def test_leave_one_out_fit_callTwiceOnDifferentData_ExpectRefit(self):
        x_a = pd.DataFrame(data=['1', '2', '2', '2', '2', '2'], columns=['col_a'])
        x_b = pd.DataFrame(data=['1', '1', '1', '2', '2', '2'], columns=['col_b'])  # different values and name
        y_dummy = [True, False, True, False, True, False]
        encoder = encoders.LeaveOneOutEncoder()
        encoder.fit(x_a, y_dummy)
        encoder.fit(x_b, y_dummy)
        mapping = encoder.mapping
        self.assertEqual(1, len(mapping))
        col_b_mapping = mapping[0]
        self.assertEqual('col_b', col_b_mapping['col']) # the model must get updated
        self.assertEqual({'sum': 2.0, 'count': 3, 'mean': 2.0/3.0}, col_b_mapping['mapping']['1'])
        self.assertEqual({'sum': 1.0, 'count': 3, 'mean': 01.0/3.0}, col_b_mapping['mapping']['2'])

    def test_one_hot(self):
        enc = encoders.OneHotEncoder(verbose=1, return_df=False)
        enc.fit(X)
        self.assertEqual(enc.transform(X_t).shape[1],
                         enc.transform(X_t[X_t['extra'] != 'A']).shape[1],
                         'We have to get the same count of columns')

        enc = encoders.OneHotEncoder(verbose=1, return_df=True, impute_missing=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertIn('extra_-1', out.columns.values)

        enc = encoders.OneHotEncoder(verbose=1, return_df=True, impute_missing=True, handle_unknown='ignore')
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertEqual(len([x for x in out.columns.values if str(x).startswith('extra_')]), 3)

        enc = encoders.OneHotEncoder(verbose=1, return_df=True, impute_missing=True, handle_unknown='error')
        enc.fit(X)
        with self.assertRaises(ValueError):
            out = enc.transform(X_t)

        enc = encoders.OneHotEncoder(verbose=1, return_df=True, handle_unknown='ignore', use_cat_names=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertIn('extra_A', out.columns.values)

        enc = encoders.OneHotEncoder(verbose=1, return_df=True, use_cat_names=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertIn('extra_-1', out.columns.values)

        # test inverse_transform
        X_i = tu.create_dataset(n_rows=100, has_none=False)
        X_i_t = tu.create_dataset(n_rows=50, has_none=False)
        X_i_t_extra = tu.create_dataset(n_rows=50, extras=True, has_none=False)
        cols = ['underscore', 'none', 'extra', 321]

        enc = encoders.OneHotEncoder(verbose=1, use_cat_names=True, cols=cols)
        enc.fit(X_i)
        obtained = enc.inverse_transform(enc.transform(X_i_t))
        obtained[321] = obtained[321].astype('int64')   # numeric columns are incorrectly typed as object...
        verify_inverse_transform(X_i_t, obtained)

    def test_ordinal(self):

        enc = encoders.OrdinalEncoder(verbose=1, return_df=True, impute_missing=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertEqual(len(set(out['extra'].values)), 4)
        self.assertIn(0, set(out['extra'].values))
        self.assertFalse(enc.mapping is None)
        self.assertTrue(len(enc.mapping) > 0)

        enc = encoders.OrdinalEncoder(verbose=1, mapping=enc.mapping, return_df=True, impute_missing=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertEqual(len(set(out['extra'].values)), 4)
        self.assertIn(0, set(out['extra'].values))
        self.assertTrue(len(enc.mapping) > 0)

        enc = encoders.OrdinalEncoder(verbose=1, return_df=True, impute_missing=True, handle_unknown='ignore')
        enc.fit(X)
        out = enc.transform(X_t)
        out_cats = [x for x in set(out['extra'].values) if np.isfinite(x)]
        self.assertEqual(len(out_cats), 3)
        self.assertFalse(enc.mapping is None)

    def test_ordinal_dist(self):
        data = np.array([
            ['apple', None],
            ['peach', 'lemon']
        ])
        encoder = encoders.OrdinalEncoder(impute_missing=True)
        encoder.fit(data)
        a = encoder.transform(data)
        self.assertEqual(a.values[0, 1], 0)
        self.assertEqual(a.values[1, 1], 1)

        encoder = encoders.OrdinalEncoder(impute_missing=False)
        encoder.fit(data)
        a = encoder.transform(data)
        self.assertTrue(np.isnan(a.values[0, 1]))
        self.assertEqual(a.values[1, 1], 1)

    # beware: for some reason doctest does not raise exceptions - you have to read the text output
    def test_doc(self):
        suite = TestSuite()

        for filename in os.listdir('../'):
            if filename.endswith(".py"):
                suite.addTest(doctest.DocFileSuite('../' + filename))

        runner = TextTestRunner(verbosity=2)
        runner.run(suite)
