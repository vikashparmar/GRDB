#! /bin/bash

# manually add 'bin' to PATH in case it does not have it (for bash)
export PATH=/usr/local/bin:$PATH

# Read command line arguments
if [[ $# -eq 0 ]]; then
  echo "No arguments found, using default environment"
  environment="dev"
else
  echo "using environment: $1"
  environment=$1
fi

# Read configs from config file
aws_region=$(jq '.awsRegion' config/"$environment.json")
aws_region=$(echo "$aws_region" | tr -d '"')

initial_file_upload_bucket=$(jq '.initialUploadBucket' config/"$environment.json")
initial_file_upload_bucket=$(echo "$initial_file_upload_bucket" | tr -d '"')

file_upload_bucket=$(jq '.fileUploadBucket' config/"$environment.json")
file_upload_bucket=$(echo "$file_upload_bucket" | tr -d '"')

# Setting variable values for terraform
export AWS_PROFILE=$environment
export TF_VAR_region_name=$aws_region

# Delete AWS services
echo "Deleting serverless lambda execution role"
terraform -chdir=../terraform/lambda_role destroy --auto-approve || true

echo "Destroying VPC peer connection"
terraform -chdir=../terraform/vpc_peer destroy --auto-approve || true

echo "Deleting Cluster Auto Scaler"
terraform -chdir=../terraform/cas destroy --auto-approve || true

echo "Deleting AWS EKS Cluster..."
terraform -chdir=../terraform/eks-cluster destroy --auto-approve || true

#echo "Deleting SFTP Server"
#terraform -chdir=../terraform/sftp/aws-sftp-server destroy --auto-approve

echo "Deleting Cloudfront distribution"
terraform -chdir=../terraform/cloudfront destroy --auto-approve || true

# Show message
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "     KUBERNETES DESTRUCTION COMPLETE!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""

sudo rm ../terraform/cas/terraform.tfstate
sudo rm ../terraform/cas/terraform.tfstate.backup
sudo rm ../terraform/cloudfront/terraform.tfstate
sudo rm ../terraform/cloudfront/terraform.tfstate.backup
sudo rm ../terraform/eks-cluster/terraform.tfstate
sudo rm ../terraform/eks-cluster/terraform.tfstate.backup
sudo rm ../terraform/lambda_role/terraform.tfstate
sudo rm ../terraform/lambda_role/terraform.tfstate.backup
sudo rm ../terraform/vpc_peer/terraform.tfstate
sudo rm ../terraform/vpc_peer/terraform.tfstate.backup
sudo rm -rf ../terraform/cas/.terraform
sudo rm -rf ../terraform/cloudfront/.terraform
sudo rm -rf ../terraform/eks-cluster/.terraform
sudo rm -rf ../terraform/lambda_role/.terraform
sudo rm -rf ../terraform/vpc_peer/.terraform

# Show message
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "      TERRAFORM DESTRUCTION COMPLETE!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""
