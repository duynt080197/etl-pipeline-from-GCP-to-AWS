variable "aws_region" {
  description = "The AWS region to create things in."
  default     = "us-east-1"
} 
variable "access_key" {
  description = "AWS Access key"
  default     = "AKIA2NVTRKO5YHQK3MB5"
} 
variable "secret_key" {
  description = "AWS Secret key"
  default     = "v5G4ODW3XpPSK9XgdK8/O1q9ecV+9+53VfL6lfpE"
} 

variable "network_interface_id" {
  type = string
  default = "vpc-0b8d646095e797eb5"
}

variable "ami" {
    type = string
    default = "ami-0cff7528ff583bf9a"
}

variable "instance_type" {
    type = string
    default = "t2.micro"
}