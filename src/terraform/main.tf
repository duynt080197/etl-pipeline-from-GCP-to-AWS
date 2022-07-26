provider "aws" {
   region = var.aws_region
  access_key = var.access_key
  secret_key = var.secret_key
}
provider "archive" {}

data "archive_file" "zip" {
  type        = "zip"
  source_file = "../main/ingest_data_from_gcs_to_s3.py"
  output_path = "output/ingest_data_from_gcs_to_s3.zip"
}
data "archive_file" "zip1" {
  type        = "zip"
  source_file = "../main/cleaning_data.py"
  output_path = "output/cleaning_data.zip"
}
data "archive_file" "execute_ec2" {
  type        = "zip"
  source_file = "../main/execute_ec2.py"
  output_path = "output/execute_ec2.zip"
}


resource "aws_iam_role" "iam_role_gcs_to_s3" {
  name               = "iam_role_gcs_to_s3"
  assume_role_policy = jsonencode(
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]}
  )
}
resource "aws_iam_role_policy_attachment" "attach-s3" {
  role       = aws_iam_role.iam_role_gcs_to_s3.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
resource "aws_iam_role_policy_attachment" "attach-ssm" {
  role       = aws_iam_role.iam_role_gcs_to_s3.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}
resource "aws_iam_role_policy_attachment" "attach-ec2" {
  role       = aws_iam_role.iam_role_gcs_to_s3.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}
resource "aws_iam_role_policy_attachment" "attach-lambda-execute" {
  role       = aws_iam_role.iam_role_gcs_to_s3.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}
resource "aws_iam_role_policy_attachment" "attach-admin-access" {
  role       = aws_iam_role.iam_role_gcs_to_s3.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_lambda_function" "lambda" {
  function_name = "ingest_data_from_gcs_to_s3"

  filename         = "${data.archive_file.zip.output_path}"
  source_code_hash = "${data.archive_file.zip.output_base64sha256}"

  role    = "${aws_iam_role.iam_role_gcs_to_s3.arn}"
  handler = "ingest_data_from_gcs_to_s3.lambda_handler"
  runtime = "python3.7"
  layers = ["arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPython:26"]
  timeout = 120
  
}
resource "aws_lambda_function" "lambda1" {
  function_name = "cleaning_data"

  filename         = "${data.archive_file.zip1.output_path}"
  source_code_hash = "${data.archive_file.zip1.output_base64sha256}"

  role    = "${aws_iam_role.iam_role_gcs_to_s3.arn}"
  handler = "cleaning_data.lambda_handler"
  runtime = "python3.7"
  layers = ["arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPython:26"]
  timeout = 120
  
}
resource "aws_lambda_function" "execute_ec2" {
  function_name = "execute_ec2"

  filename         = "${data.archive_file.execute_ec2.output_path}"
  source_code_hash = "${data.archive_file.execute_ec2.output_base64sha256}"

  role    = "${aws_iam_role.iam_role_gcs_to_s3.arn}"
  handler = "execute_ec2.lambda_handler"
  runtime = "python3.7"
  layers = ["arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPython:26"]
  timeout = 120
  
}
resource "aws_instance" "ec2" {
  ami           = var.ami
  instance_type = var.instance_type
}