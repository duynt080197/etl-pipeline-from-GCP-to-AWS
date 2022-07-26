import sys
from unittest import result
sys.path.insert(0, '../src')
import unittest
import os
import boto3
from unittest.mock import patch
from main import cleaning_data
import pandas as pd
import numpy as np

class TestCleaningData(unittest.TestCase):
    def test_get_list_object_from_s3(self):
        result = cleaning_data.get_list_object_from_s3('asdsa112')['Contents'][0]['Key']
        print(result)
        self.assertEqual(result, 'demo.txt')

    #@patch.dict(cleaning_data.get_list_object_from_s3, {'Contents':[{'Key': 'test.txt'}]})
    @patch.object(cleaning_data, 'get_list_object_from_s3')
    def test_read_object_to_df(self, test_get_list_object_from_s3):
        test_get_list_object_from_s3.return_value = {'Contents':[{'Key': 'test.csv'}]}
        result = cleaning_data.read_object_to_df('test-569')
        result = result.to_dict()
        print('xx',result)
        print(type(result))
        expected_df = {'column1,column2': {0: 'row1,row2'}}
        self.assertEqual(result, expected_df)

    def test_delete_duplicate_and_remove_nan_value(self):
        data = {'col_1': ['row1', 'row2', 'row1'], 'country': ['row1', np.nan, 'row1']}
        test_df = pd.DataFrame.from_dict(data)
        df = cleaning_data.delete_duplicate(test_df)
        cleaning_data.replace_nan_value_in_country_col(df)
        result = df.to_dict()
        print('s', result)
        expected_result = {'col_1': {0: 'row1', 1: 'row2'}, 'country': {0: 'row1', 1: 'Unknown'}}
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()