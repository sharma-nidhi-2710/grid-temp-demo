#!/bin/bash

# Grid Temperature Forecasting - EKS Deployment Script
# Replace these variables with your actual values

AWS_ACCOUNT_ID="YOUR_AWS_ACCOUNT_ID"
AWS_REGION="us-west-2"
ECR_REPO_NAME="grid-temp-forecasting"
IMAGE_TAG="latest"

# Full ECR image URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}"

echo "=== Step 1: Create ECR Repository (if not exists) ==="
aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || echo "Repository already exists"

echo "=== Step 2: Authenticate Docker to ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo "=== Step 3: Build Docker Image ==="
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

echo "=== Step 4: Tag Image for ECR ==="
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}

echo "=== Step 5: Push Image to ECR ==="
docker push ${ECR_URI}

echo "=== Step 6: Update Kubernetes Deployment with ECR URI ==="
sed -i "s|<AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/grid-temp-forecasting:latest|${ECR_URI}|g" k8s/deployment.yaml

echo "=== Step 7: Deploy to EKS ==="
kubectl apply -f k8s/deployment.yaml

echo "=== Step 8: Check Deployment Status ==="
kubectl rollout status deployment/grid-temp-forecasting

echo "=== Step 9: Get Service External IP ==="
kubectl get service grid-temp-forecasting-service

echo ""
echo "Deployment complete! Once the LoadBalancer is ready, you can access the API at:"
echo "http://<EXTERNAL-IP>/predict"
echo "http://<EXTERNAL-IP>/health"
echo "http://<EXTERNAL-IP>/docs  (Swagger UI)"
