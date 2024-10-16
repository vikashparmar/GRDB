#! /bin/bash

# Read command line arguments
if [[ $# -eq 0 ]]; then
  echo "No arguments found, using default resource_name: grdb, environment: dev"
  resource_name="grdb"
  environment="dev"
else
  echo "using resource_name: $1"
  echo "using environment: $2"
  resource_name=$1
  environment=$2
fi

# Read configs from config file
aws_region=$(jq '.awsRegion' config/"$environment.json")
aws_region=$(echo "$aws_region" | tr -d '"')

aws_access_key_id=$(jq '.accessKeyId' config/"deployment.json")
aws_access_key_id=$(echo "$aws_access_key_id" | tr -d '"')

aws_secret_access_key=$(jq '.secretAccessKey' config/"deployment.json")
aws_secret_access_key=$(echo "$aws_secret_access_key" | tr -d '"')

file_upload_bucket=$(jq '.initialUploadBucket' config/"$environment.json")
file_upload_bucket=$(echo "$file_upload_bucket" | tr -d '"')

rds_vpc_id=$(jq '.rdsVpcId' config/"$environment.json")
rds_vpc_id=$(echo "$rds_vpc_id" | tr -d '"')

rds_vpc_cidr=$(jq '.rdsVpcCidr' config/"$environment.json")
rds_vpc_cidr=$(echo "$rds_vpc_cidr" | tr -d '"')

rds_vpc_route_table_id=$(jq '.rdsVpcRouteTableId' config/"$environment.json")
rds_vpc_route_table_id=$(echo "$rds_vpc_route_table_id" | tr -d '"')

ecr_repository=$(jq '.ecrRepository' config/"$environment.json")
ecr_repository=$(echo "$ecr_repository" | tr -d '"')

aws_region=$(jq '.awsRegion' config/"$environment.json")
aws_region=$(echo "$aws_region" | tr -d '"')

# Setting variable values for terraform
export AWS_PROFILE=$environment
export TF_VAR_resource_name=$resource_name
export TF_VAR_region_name=$aws_region
export TF_VAR_environment=$environment
export TF_VAR_file_upload_bucket=$file_upload_bucket
export TF_VAR_access_key_id=$aws_access_key_id
export TF_VAR_secret_access_key=$aws_secret_access_key
export TF_VAR_vpc_rds_id=$rds_vpc_id
export TF_VAR_vpc_rds_cidr=$rds_vpc_cidr
export TF_VAR_default_route_table_id_rds_vpc=$rds_vpc_route_table_id
npm i


image_name="grdb"
tag="latest"

# Authenticating docker with ECR
aws ecr get-login-password --region "$aws_region" | docker login --username AWS --password-stdin "$ecr_repository"

# Building image
docker build -t "$ecr_repository/$image_name:$tag" ../

# Pushing image to ECR
docker push "$ecr_repository/$image_name:$tag"


cluster_id=$(terraform -chdir=../terraform/eks-cluster output cluster_id)
cluster_id=$(echo "$cluster_id" | tr -d '"')

cluster_name=$(terraform -chdir=../terraform/eks-cluster output cluster_name)
cluster_name=$(echo "$cluster_name" | tr -d '"')

echo "Updating kubernetes config"
aws eks --region "$aws_region" update-kubeconfig --name "$cluster_name"

# Creating WPA
set -e

wpa_tag_name=$(curl -s https://api.github.com/repos/practo/k8s-worker-pod-autoscaler/releases/latest | python -c "import json;import sys;sys.stdout.write(json.load(sys.stdin)['tag_name']+'\n')")
export WPA_TAG=$wpa_tag_name

new_deployment='../terraform/wpa/deployment.yaml'
template_deployment='../terraform/wpa/deployment-template.yaml'
wpa_deployment="../terraform/wpa/wpa_${environment}.yaml"
main_deployment="../terraform/wpa/sqs-consumer-deployment_${environment}.yaml"

echo "Generating Deployment Manifest..."
aws_region=$(echo "$aws_region" | tr -d '"')
aws_access_key_id=$(echo "$aws_access_key_id" | tr -d '"')
aws_secret_access_key=$(echo "$aws_secret_access_key" | tr -d '"')

export AWS_REGIONS=$aws_region
export AWS_ACCESS_KEY_ID=$aws_access_key_id
export AWS_SECRET_ACCESS_KEY=$aws_secret_access_key

export WPA_AWS_REGIONS=$aws_region
export WPA_AWS_ACCESS_KEY_ID=$aws_access_key_id
export WPA_AWS_SECRET_ACCESS_KEY=$aws_secret_access_key

cp -f $template_deployment $new_deployment
bash ../terraform/wpa/generate.sh ${new_deployment}

kubectl replace -f ${new_deployment}
kubectl replace -f "${main_deployment}"
kubectl replace -f "${wpa_deployment}"
echo "Successfully updated WPA"

echo "Deleting SFTP Server"
terraform -chdir=../terraform/sftp/aws-sftp-server init
terraform -chdir=../terraform/sftp/aws-sftp-server destroy --auto-approve

# Deploying SFTP server
echo "Creating SFTP Server"
terraform -chdir=../terraform/sftp/aws-sftp-server init
terraform -chdir=../terraform/sftp/aws-sftp-server apply --auto-approve

sftp_server_id=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_server_id)
server_id=$(echo "$sftp_server_id" | tr -d '"')

aws_sftp_with_password_endpoint=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_with_password_endpoint)
aws_sftp_with_ssh_endpoint=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_with_ssh_endpoint)
echo "SFTP Server with password: $aws_sftp_with_password_endpoint"
echo "SFTP Server with ssh key: $aws_sftp_with_ssh_endpoint"

# Change config file to add config values
echo "Editing config file"
python3 start_util.py "$server_id" "$resource_name" "$environment" "" "" ""

# Deploying serverless application
echo "Deploying serverless application"
sls deploy --stage "$environment"