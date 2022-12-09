provider "aws" {
  region = "eu-central-1"
}
terraform {
  backend "s3" {
    region = "eu-central-1"
    bucket = "p-kuligowski-bucket"
    key    = "p-kuligowski-bucket/tmobile.tfstate"
  }
}
