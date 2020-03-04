import numpy as np
import pandas as pd
from unittest2 import TestCase
from sklearn.model_selection import GroupKFold

import category_encoders as encoders
import category_encoders.tests.helpers as th
from category_encoders.wrapper import MultiClassWrapper, NestedCVWrapper


class TestMultiClassWrapper(TestCase):
    def test_invariance_to_data_types(self):
        x = np.array([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
        ])
        y = [1, 2, 3, 3, 3, 3]
        wrapper = MultiClassWrapper(encoders.TargetEncoder())
        result = wrapper.fit_transform(x, y)
        th.verify_numeric(result)

        x = pd.DataFrame([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
        ], columns=['f1', 'f2', 'f3'])
        y = ['bee', 'cat', 'dog', 'dog', 'dog', 'dog']
        wrapper = MultiClassWrapper(encoders.TargetEncoder())
        result2 = wrapper.fit_transform(x, y)

        self.assertTrue((result.values == result2.values).all(), 'The content should be the same regardless whether we pass Numpy or Pandas data type.')

    def test_transform_only_selected(self):
        x = pd.DataFrame([
            ['a', 'b', 'c'],
            ['a', 'a', 'c'],
            ['b', 'a', 'c'],
            ['b', 'c', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
        ], columns=['f1', 'f2', 'f3'])
        y = ['bee', 'cat', 'dog', 'dog', 'dog', 'dog']
        wrapper = MultiClassWrapper(encoders.LeaveOneOutEncoder(cols=['f2']))

        # combination fit() + transform()
        wrapper.fit(x, y)
        result = wrapper.transform(x)
        print(result)
        self.assertEqual(len(result.columns), 4, 'We expect 2 untouched features + f2 target encoded into 2 features')

        # directly fit_transform()
        wrapper = MultiClassWrapper(encoders.LeaveOneOutEncoder(cols=['f2']))
        result2 = wrapper.fit_transform(x, y)
        print(result2)
        self.assertEqual(len(result2.columns), 4, 'We expect 2 untouched features + f2 target encoded into 2 features')

        # in the case of leave-one-out, we expect different results, because leave-one-out principle
        # is applied only on the training data (to decrease overfitting) while the testing data
        # use the whole statistics (to be as accurate as possible).
        self.assertFalse(result.iloc[0, 3] == result2.iloc[0, 3])


class TestNestedCVWrapper(TestCase):
    def test_invariance_to_data_types(self):
        x = np.array([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
        ])
        y = [1, 2, 3, 3, 3, 3]
        wrapper = NestedCVWrapper(encoders.TargetEncoder(), cv=2)
        result = wrapper.fit_transform(x, y)
        th.verify_numeric(result)

        x = pd.DataFrame([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
        ], columns=['f1', 'f2', 'f3'])
        y = ['bee', 'cat', 'dog', 'dog', 'dog', 'dog']
        wrapper = NestedCVWrapper(encoders.TargetEncoder(), cv=2)
        result2 = wrapper.fit_transform(x, y)

        self.assertTrue((result.values == result2.values).all(), 'The content should be the same regardless whether we pass Numpy or Pandas data type.')

    def test_train_not_equal_to_valid(self):
        x = np.array([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
            ['a', 'b', 'a'],
        ])
        y = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
        wrapper = NestedCVWrapper(encoders.TargetEncoder(), cv=3)
        result_train, result_valid = wrapper.fit_transform(x, y, X_test=x)

        # We would expect result_train != result_valid since result_train has been generated using nested
        # folds and result_valid is generated by fitting the encoder on all of the x & y daya
        self.assertFalse(np.allclose(result_train, result_valid))


    def test_custom_cv(self):
        x = np.array([
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'c'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['b', 'b', 'b'],
            ['a', 'b', 'a'],
            ['a', 'b', 'a'],
        ])
        groups = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
        y = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
        gkfold = GroupKFold(n_splits=3)
        wrapper = NestedCVWrapper(encoders.TargetEncoder(), cv=gkfold)
        result_train, result_valid = wrapper.fit_transform(x, y, X_test=x, groups=groups)

        # We would expect result_train != result_valid since result_train has been generated using nested
        # folds and result_valid is generated by fitting the encoder on all of the x & y daya
        self.assertFalse(np.allclose(result_train, result_valid))
