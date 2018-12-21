import pandas as pd
from unittest2 import TestCase  # or `from unittest import ...` if on Python 3.4+
import numpy as np
import category_encoders as encoders


class TestBaseNEncoder(TestCase):

    def test_fit_transform_have_base_2_expect_Correct_Encoding(self):
        train = pd.Series(['a', 'b', 'c', 'd'])

        result = encoders.BaseNEncoder(base=2).fit_transform(train)

        self.assertEqual(4, result.shape[0])
        self.assertListEqual([0, 0, 1], result.iloc[0, :].tolist())
        self.assertListEqual([0, 1, 0], result.iloc[1, :].tolist())
        self.assertListEqual([0, 1, 1], result.iloc[2, :].tolist())
        self.assertListEqual([1, 0, 0], result.iloc[3, :].tolist())

    def test_inverse_transform_HaveData_ExpectResultReturned(self):
        train = pd.Series(list('abcd')).to_frame('letter')

        enc = encoders.BaseNEncoder(base=2)
        result = enc.fit_transform(train)
        inversed_result = enc.inverse_transform(result)

        pd.testing.assert_frame_equal(train, inversed_result)

    def test_HaveIndicatorAndNanValue_ExpectNewColumn(self):
        train = pd.Series(['a', 'b', 'c', np.nan])

        result = encoders.BaseNEncoder(handle_missing='indicator', base=2).fit_transform(train)

        self.assertEqual(4, result.shape[0])
        self.assertListEqual([0, 0, 1], result.iloc[0, :].tolist())
        self.assertListEqual([0, 1, 0], result.iloc[1, :].tolist())
        self.assertListEqual([0, 1, 1], result.iloc[2, :].tolist())
        self.assertListEqual([1, 0, 0], result.iloc[3, :].tolist())

    def test_HandleMissingIndicator_HaveNoNan_ExpectThirdColumn(self):
        train = pd.Series(['a', 'b', 'c'])

        result = encoders.BaseNEncoder(handle_missing='indicator', base=2).fit_transform(train)

        self.assertEqual(3, result.shape[0])
        self.assertListEqual([0, 0, 1], result.iloc[0, :].tolist())
        self.assertListEqual([0, 1, 0], result.iloc[1, :].tolist())
        self.assertListEqual([0, 1, 1], result.iloc[2, :].tolist())

    def test_HandleMissingIndicator_NanNoNanInTrain_ExpectAsNanColumn(self):
        train = pd.Series(['a', 'b', 'c'])
        test = pd.Series(['a', 'b', 'c', np.nan])

        encoder = encoders.BaseNEncoder(handle_missing='indicator')
        encoder.fit(train)
        result = encoder.transform(test)

        self.assertEqual(4, result.shape[0])
        self.assertListEqual([0, 0, 1], result.iloc[0, :].tolist())
        self.assertListEqual([0, 1, 0], result.iloc[1, :].tolist())
        self.assertListEqual([0, 1, 1], result.iloc[2, :].tolist())
        self.assertListEqual([1, 0, 0], result.iloc[3, :].tolist())

    # def test_HandleUnknown_HaveNoUnknownInTrain_ExpectIndicatorInTest(self):
    #     train = ['A', 'B']
    #     test = ['A', 'B', 'C']
    #
    #     encoder = encoders.BaseNEncoder(handle_unknown='indicator')
    #     encoder.fit(train)
    #     result = encoder.transform(test)
    #
    #     expected = [[1, -2 / 3.0, -1 / 3.0],
    #                 [1, 1 / 3.0, -1 / 3.0],
    #                 [1, 1 / 3.0, 2 / 3.0]]
    #     self.assertEqual(result.values.tolist(), expected)
    #
    # def test_HandleUnknown_HaveOnlyKnown_ExpectSecondColumn(self):
    #     train = ['A', 'B']
    #
    #     encoder = encoders.BaseNEncoder(handle_unknown='indicator')
    #     result = encoder.fit_transform(train)
    #
    #     expected = [[1, -2 / 3.0, -1 / 3.0],
    #                 [1, 1 / 3.0, -1 / 3.0]]
    #     self.assertEqual(result.values.tolist(), expected)
