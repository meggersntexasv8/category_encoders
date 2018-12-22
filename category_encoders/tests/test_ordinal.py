import pandas as pd
from unittest2 import TestCase  # or `from unittest import ...` if on Python 3.4+
import category_encoders.tests.test_utils as tu
import numpy as np

import category_encoders as encoders


np_X = tu.create_array(n_rows=100)
np_X_t = tu.create_array(n_rows=50, extras=True)
np_y = np.random.randn(np_X.shape[0]) > 0.5
np_y_t = np.random.randn(np_X_t.shape[0]) > 0.5
X = tu.create_dataset(n_rows=100)
X_t = tu.create_dataset(n_rows=50, extras=True)
y = pd.DataFrame(np_y)
y_t = pd.DataFrame(np_y_t)


class TestOrdinalEncoder(TestCase):

    def test_ordinal(self):

        enc = encoders.OrdinalEncoder(verbose=1, return_df=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertEqual(len(set(out['extra'].values)), 4)
        self.assertIn(-1, set(out['extra'].values))
        self.assertFalse(enc.mapping is None)
        self.assertTrue(len(enc.mapping) > 0)

        enc = encoders.OrdinalEncoder(verbose=1, mapping=enc.mapping, return_df=True)
        enc.fit(X)
        out = enc.transform(X_t)
        self.assertEqual(len(set(out['extra'].values)), 4)
        self.assertIn(-1, set(out['extra'].values))
        self.assertTrue(len(enc.mapping) > 0)

        enc = encoders.OrdinalEncoder(verbose=1, return_df=True, handle_unknown='return _nan')
        enc.fit(X)
        out = enc.transform(X_t)
        out_cats = [x for x in set(out['extra'].values) if np.isfinite(x)]
        self.assertEqual(len(out_cats), 3)
        self.assertFalse(enc.mapping is None)

    def test_ordinal_dist(self):
        data = np.array([
            ['apple', 'lemon'],
            ['peach', None]
        ])
        encoder = encoders.OrdinalEncoder()
        result = encoder.fit_transform(data)
        self.assertEqual(2, len(result[0].unique()), "We expect two unique values in the column")
        self.assertEqual(2, len(result[1].unique()), "We expect two unique values in the column")
        self.assertFalse(np.isnan(result.values[1, 1]))

        encoder = encoders.OrdinalEncoder(handle_missing='return_nan')
        result = encoder.fit_transform(data)
        self.assertEqual(2, len(result[0].unique()), "We expect two unique values in the column")
        self.assertEqual(2, len(result[1].unique()), "We expect two unique values in the column")

    def test_pandas_categorical(self):
        X = pd.DataFrame({
            'Str': ['a', 'c', 'c', 'd'],
            'Categorical': pd.Categorical(list('bbea'), categories=['e', 'a', 'b'], ordered=True)
        })

        enc = encoders.OrdinalEncoder()
        out = enc.fit_transform(X)

        tu.verify_numeric(out)
        self.assertEqual(3, out['Categorical'][0])
        self.assertEqual(3, out['Categorical'][1])
        self.assertEqual(1, out['Categorical'][2])
        self.assertEqual(2, out['Categorical'][3])

    def test_handle_missing_have_nan_fit_time_expect_as_category(self):
        train = pd.DataFrame({'city': ['chicago', np.nan]})

        enc = encoders.OrdinalEncoder(handle_missing='value')
        out = enc.fit_transform(train)

        self.assertListEqual([1, 2], out['city'].tolist())

    def test_handle_missing_have_nan_transform_time_expect_negative_2(self):
        train = pd.DataFrame({'city': ['chicago', 'st louis']})
        test = pd.DataFrame({'city': ['chicago', np.nan]})

        enc = encoders.OrdinalEncoder(handle_missing='value')
        enc.fit(train)
        out = enc.transform(test)

        self.assertListEqual([1, -2], out['city'].tolist())

    def test_handle_unknown_have_new_value_expect_negative_1(self):
        train = pd.DataFrame({'city': ['chicago', 'st louis']})
        test = pd.DataFrame({'city': ['chicago', 'los angeles']})
        expected = [1.0, -1.0]

        enc = encoders.OrdinalEncoder(handle_missing='return_nan')
        enc.fit(train)
        result = enc.transform(test)['city'].tolist()

        self.assertEqual(expected, result)

    def test_HaveNegativeOneInTrain_ExpectCodedAsOne(self):
        train = pd.DataFrame({'city': [-1]})
        expected = [1]

        enc = encoders.OrdinalEncoder(cols=['city'])
        result = enc.fit_transform(train)['city'].tolist()

        self.assertEqual(expected, result)

    def test_HaveNaNInTrain_ExpectCodedAsOne(self):
        train = pd.DataFrame({'city': [np.nan]})
        expected = [1]

        enc = encoders.OrdinalEncoder(cols=['city'])
        result = enc.fit_transform(train)['city'].tolist()

        self.assertEqual(expected, result)

    def test_HaveNoneAndNan_ExpectCodesAsOne(self):
        train = pd.DataFrame({'city': [np.nan, None]})
        expected = [1, 1]

        enc = encoders.OrdinalEncoder(cols=['city'])
        result = enc.fit_transform(train)['city'].tolist()

        self.assertEqual(expected, result)
