provider "aws" {
  region = "eu-central-1"
}
terraform {
  backend "s3" {
    region = "eu-central-1"
    bucket = "s3-bucket"
    key    = "s3-bucket/tmobile.tfstate"
  }
}
