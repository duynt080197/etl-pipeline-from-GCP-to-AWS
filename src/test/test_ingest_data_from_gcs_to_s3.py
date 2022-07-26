import sys
from unittest import result
sys.path.insert(0, '../src')
import unittest
import os
import boto3
from unittest.mock import patch
from main import ingest_data_from_gcs_to_s3

class TestIngestDataGcsToS3(unittest.TestCase):
    #@patch.object(ingest_data_from_gcs_to_s3, 'get_parameter_store')
    def test_get_parameter_store(self):
        expected_param = 'duynt71'
        test_parameter = ingest_data_from_gcs_to_s3.get_parameter_store('s3_bucket')
        self.assertEqual(test_parameter, expected_param)

    def test_get_client_s3_for_gcs(self):
        result = ingest_data_from_gcs_to_s3.get_client_s3_for_gcs().list_objects_v2(Bucket='demo-duynt39')['Contents'][0]['Key']
        print("xx",result)
        expected_result = 'demo.txt'
        self.assertEqual(result, expected_result)
    
    @patch.dict(os.environ, {"AWS_LAMBDA_LOG_GROUP_NAME": "/aws/lambda/s3-to-gcs", "AWS_REGION": "us-east-1", "AWS_LAMBDA_LOG_STREAM_NAME": "2022/07/25/[$LATEST]a42d11d4fb5d4abd98e1496284885ce1"})
    def test_get_current_log_group_name(self):
        result1 = ingest_data_from_gcs_to_s3.get_current_log_group_name()
        result2 = ingest_data_from_gcs_to_s3.get_current_region()
        result3 = ingest_data_from_gcs_to_s3.get_current_log_stream_name()
        
        expected1 = '/aws/lambda/s3-to-gcs'
        expected2 = 'us-east-1'
        expected3 = '2022/07/25/[$LATEST]a42d11d4fb5d4abd98e1496284885ce1'
        self.assertEqual(result1, expected1)
        self.assertEqual(result2, expected2)
        self.assertEqual(result3, expected3)

    @patch.object(ingest_data_from_gcs_to_s3,'get_parameter_store')
    @patch.object(ingest_data_from_gcs_to_s3,'get_current_log_stream_name')    
    @patch.object(ingest_data_from_gcs_to_s3,'get_current_region')
    @patch.object(ingest_data_from_gcs_to_s3, 'get_current_log_group_name')    
    def test_send_alert(self, test_get_parameter_store, test_get_current_log_group_name, test_get_current_region, test_get_current_log_stream_name):
        test_get_current_log_group_name.return_value = '/aws/lambda/s3-to-gcs'
        test_get_current_region.return_value = 'us-east-1'
        test_get_current_log_stream_name.return_value = 'http://google.com.vn'
        
        test_get_parameter_store.return_value = 'https://hooks.slack.com/services/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'
        with patch('requests.post') as patched_post:
            patched_post.return_value = True
        result = ingest_data_from_gcs_to_s3.send_alert('test','1','2','3','4')
        self.assertEqual(result, 'success')
    
    def test_get_object_from_gcs_to_s3(self):
        s3_client_test = boto3.client('s3')
        s3_client_test.delete_object(Bucket='asdsa112', Key='demo.txt')
        ingest_data_from_gcs_to_s3.get_object_from_gcs_to_s3('asdsa112', 'demo-duynt39')
        result_file = s3_client_test.list_objects_v2(Bucket='asdsa112')['Contents'][0]['Key']
        self.assertEqual(result_file, 'demo.txt')

        
if __name__ == '__main__':
    unittest.main()