#! /bin/bash
# Script to update WPA configuration

# Read command line arguments
if [[ $# -eq 0 ]]; then
  echo "No arguments found, using default environment: dev"
  environment="dev"
else
  echo "using environment: $1"
  environment=$1
fi

wpa_deployment="../terraform/wpa/wpa_${environment}.yaml"
kubectl replace -f "${wpa_deployment}"