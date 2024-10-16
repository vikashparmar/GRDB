#! /bin/bash

# manually add 'bin' to PATH in case it does not have it (for bash)
export PATH=/usr/local/bin:$PATH



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

echo "------------------------------------------------------------------------"
echo "STARTED DEPLOYMENT SCRIPT, CHECKING INSTALLED TOOLS"
echo "------------------------------------------------------------------------"

# check if all the required programs are installed or not
if ! node --version
then 
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'node' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! npm --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'npm' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! python --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'python' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! serverless --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'serverless' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! aws --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'aws' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! docker --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'docker' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! terraform --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'terraform' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! kubectl --help > /dev/null
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'kubectl' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! git --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'git' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

if ! jq --version
then
echo "-------------------------------------------------------"
echo "     REQUIRED TOOL 'jq' IS NOT INSTALLED!"
echo "-------------------------------------------------------"
exit
fi

# Show message if all the required programs are installed
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "     ALL PREREQUISITE TOOLS ARE INSTALLED!!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""

echo "------------------------------------------------------------------------"
echo "CHECKING CONFIG FILES"
echo "------------------------------------------------------------------------"

# perform checks for files exist
FILE=../sqs-listener/config.yaml
if test -f "$FILE"; then
    echo "$FILE exists."
else 
echo "------------------------------------------------------------------------------------"
echo "     REQUIRED CONFIG FILE '$FILE' DOES NOT EXIST!"
echo "------------------------------------------------------------------------------------"
exit
fi

# perform checks for files exist
FILE=config/deployment.json
if test -f "$FILE"; then
    echo "$FILE exists."
else
echo "------------------------------------------------------------------------------------"
echo "     REQUIRED CONFIG FILE '$FILE' DOES NOT EXIST!"
echo "------------------------------------------------------------------------------------"
exit
fi

# perform checks for files exist
FILE=config/$environment.json
if test -f "$FILE"; then
    echo "$FILE exists."
else
echo "------------------------------------------------------------------------------------"
echo "     REQUIRED CONFIG FILE '$FILE' DOES NOT EXIST!"
echo "------------------------------------------------------------------------------------"
exit
fi

# Show message if all the required programs are installed
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "     ALL REQUIRED CONFIGURATION FILES ARE PRESENT!!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""

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




# Creating EKS Cluster
echo "Creating AWS EKS Cluster..."
terraform -chdir=../terraform/eks-cluster init
terraform -chdir=../terraform/eks-cluster apply --auto-approve

cluster_id=$(terraform -chdir=../terraform/eks-cluster output cluster_id)
cluster_id=$(echo "$cluster_id" | tr -d '"')

cluster_name=$(terraform -chdir=../terraform/eks-cluster output cluster_name)
cluster_name=$(echo "$cluster_name" | tr -d '"')

cluster_identity_oidc_issuer=$(terraform -chdir=../terraform/eks-cluster output cluster_identity_oidc_issuer)
cluster_identity_oidc_issuer_arn=$(terraform -chdir=../terraform/eks-cluster output cluster_identity_oidc_issuer_arn)

cluster_identity_oidc_issuer=$(echo "$cluster_identity_oidc_issuer" | tr -d '"')
cluster_identity_oidc_issuer_arn=$(echo "$cluster_identity_oidc_issuer_arn" | tr -d '"')

security_group_id=$(terraform -chdir=../terraform/eks-cluster output security_group_id)
security_group_id=$(echo "$security_group_id" | tr -d '"')

private_subnet_ids=$(terraform -chdir=../terraform/eks-cluster output private_subnet_ids)
private_subnet_ids=$(echo "$private_subnet_ids" | tr -d '"')

default_route_table_id=$(terraform -chdir=../terraform/eks-cluster output default_route_table_id)
default_route_table_id=$(echo "$default_route_table_id" | tr -d '"')

public_route_table_id=$(terraform -chdir=../terraform/eks-cluster output public_route_table_id)
public_route_table_id=$(echo "$public_route_table_id" | tr -d '"')

private_route_table_id=$(terraform -chdir=../terraform/eks-cluster output private_route_table_id)
private_route_table_id=$(echo "$private_route_table_id" | tr -d '"')

vpc_id=$(terraform -chdir=../terraform/eks-cluster output vpc_id)
vpc_id=$(echo "$vpc_id" | tr -d '"')

vpc_cidr=$(terraform -chdir=../terraform/eks-cluster output vpc_cidr)
vpc_cidr=$(echo "$vpc_cidr" | tr -d '"')



# For VPC peer
export TF_VAR_vpc_eks_id=$vpc_id
export TF_VAR_private_route_table_id_eks_vpc=$private_route_table_id
export TF_VAR_public_route_table_id_eks_vpc=$public_route_table_id
export TF_VAR_default_route_table_id_eks_vpc=$default_route_table_id
export TF_VAR_vpc_eks_cidr=$vpc_cidr



# For CAS
export TF_VAR_cluster_name=$cluster_name
export TF_VAR_cluster_identity_oidc_issuer=$cluster_identity_oidc_issuer
export TF_VAR_cluster_identity_oidc_issuer_arn=$cluster_identity_oidc_issuer_arn

echo "Cluster created"

{
  echo "EKS Cluster details"
  echo "Cluster ID: $cluster_id"
  echo "Cluster Name: $cluster_name"
} >output.txt

echo "Updating kubernetes config"
aws eks --region "$aws_region" update-kubeconfig --name "$cluster_name"



# Creating WPA
set -e

wpa_tag_name=$(curl -s https://api.github.com/repos/practo/k8s-worker-pod-autoscaler/releases/latest | python -c "import json;import sys;sys.stdout.write(json.load(sys.stdin)['tag_name']+'\n')")
export WPA_TAG=$wpa_tag_name

namespace='../terraform/wpa/namespace.yaml'
crd='../terraform/wpa/crd.yaml'
service_account='../terraform/wpa/service-account.yaml'
cluster_role='../terraform/wpa/cluster-role.yaml'
cluster_role_binding='../terraform/wpa/cluster-role-binding.yaml'
new_deployment='../terraform/wpa/deployment.yaml'
template_deployment='../terraform/wpa/deployment-template.yaml'
wpa_deployment="../terraform/wpa/wpa_${environment}.yaml"
main_deployment="../terraform/wpa/sqs-consumer-deployment_${environment}.yaml"

echo "Creating CRD..."
kubectl apply -f ${crd}

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

echo "Image to be used: practodev/${WPA_TAG}"

cp -f $template_deployment $new_deployment
bash ../terraform/wpa/generate.sh ${new_deployment}

echo "Applying manifests.."
kubectl apply -f ${namespace}
kubectl apply -f ${service_account}
kubectl apply -f ${cluster_role}
kubectl apply -f ${cluster_role_binding}
kubectl apply -f ${new_deployment}
kubectl create -f "${main_deployment}"
kubectl create -f "${wpa_deployment}"
echo "Successfully created WPA"

# Deploying fluentd for logging in cloudwatch
kubectl apply -f ../terraform/wpa/k8s-log/cloudwatch-namespace.yaml

FluentBitHttpPort='2020'
FluentBitReadFromHead='Off'
[[ ${FluentBitReadFromHead} == 'On' ]] && FluentBitReadFromTail='Off' || FluentBitReadFromTail='On'
[[ -z ${FluentBitHttpPort} ]] && FluentBitHttpServer='Off' || FluentBitHttpServer='On'
kubectl create configmap fluent-bit-cluster-info \
  --from-literal=cluster.name="${cluster_name}" \
  --from-literal=http.server=${FluentBitHttpServer} \
  --from-literal=http.port=${FluentBitHttpPort} \
  --from-literal=read.head=${FluentBitReadFromHead} \
  --from-literal=read.tail=${FluentBitReadFromTail} \
  --from-literal=logs.region="${aws_region}" -n amazon-cloudwatch

kubectl apply -f ../terraform/wpa/k8s-log/fluentd.yaml

# Deploying Cluster Auto Scaler
echo "Creating Cluster Auto Scaler..."
terraform -chdir=../terraform/cas init
terraform -chdir=../terraform/cas apply --auto-approve

# Deploying VPC peer
echo "Creating VPC peer connection"
terraform -chdir=../terraform/vpc_peer init
terraform -chdir=../terraform/vpc_peer apply --auto-approve

# Change config file to add config values
echo "Editing config file"
python3 start_util.py "" "$resource_name" "$environment" "$security_group_id" "$private_subnet_ids" ""

# Show message
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "      KUBERNETES CLUSTER DEPLOYED!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""


# Deploying SFTP server
#echo "Creating SFTP Server"
#terraform -chdir=../terraform/sftp/aws-sftp-server init
#terraform -chdir=../terraform/sftp/aws-sftp-server apply --auto-approve
#
#sftp_server_id=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_server_id)
#server_id=$(echo "$sftp_server_id" | tr -d '"')
#
#aws_sftp_with_password_endpoint=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_with_password_endpoint)
#aws_sftp_with_ssh_endpoint=$(terraform -chdir=../terraform/sftp/aws-sftp-server output aws_sftp_with_ssh_endpoint)
#echo "SFTP Server with password: $aws_sftp_with_password_endpoint"
#
#{
#  echo ""
#  echo "SFTP server details"
#  echo "SFTP Server with ssh key auth: $aws_sftp_with_ssh_endpoint"
#  echo "SFTP Server with password auth: $aws_sftp_with_password_endpoint"
#} >>output.txt



# Creating IAM role for serverless lambda
terraform -chdir=../terraform/lambda_role init
terraform -chdir=../terraform/lambda_role apply --auto-approve

serverless_lambda_iam_arn=$(terraform -chdir=../terraform/lambda_role output serverless_lambda_role_arn)
serverless_lambda_iam_arn=$(echo "$serverless_lambda_iam_arn" | tr -d '"')

# Change config file to add config values
echo "Editing config file"
python3 start_util.py "" "$resource_name" "$environment" "$security_group_id" "$private_subnet_ids" "$serverless_lambda_iam_arn"

# Show message
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "         LAMBDA ROLE CREATED!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo ""






# Creating cloud front distribution
echo "Creating Cloud front distribution"

terraform -chdir=../terraform/cloudfront init
terraform -chdir=../terraform/cloudfront apply --auto-approve

website_endpoint=$(terraform -chdir=../terraform/cloudfront output dashboard_url)
website_url=$(echo "$website_endpoint" | tr -d '"')

bucket_name=$(terraform -chdir=../terraform/cloudfront output s3_bucket_id)
bucket_name=$(echo "$bucket_name" | tr -d '"')

#echo "Copying frontend code to bucket: $bucket_name"
#aws s3 cp ../terraform/cloudfront/frontend s3://"$bucket_name" --recursive
#echo "Url: $website_url"
#
#{
#  echo ""
#  echo "Cloudfront distribution details"
#  echo "Dashboard Url: $website_url"
#} >>output.txt



# Show message
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "       DASHBOARD BUCKET CREATED!"
echo "------------------------------------------"
echo ""
echo ""
echo ""
echo "------------------------------------------"
echo "       ALL COMPLETED SUCCESSFULLY!"
echo "------------------------------------------"
echo ""
echo ""
echo ""