#!/bin/bash

# Deployment script for AI services

echo "Deploying Business Management AI Services..."

# Build Docker image
echo "Building Docker image..."
docker build -t business-ai-services:latest -f deployment/docker/Dockerfile .

# Tag for registry (replace with your registry)
docker tag business-ai-services:latest your-registry.com/business-ai-services:latest

# Push to registry
echo "Pushing to registry..."
docker push your-registry.com/business-ai-services:latest

# Deploy to cloud (example for AWS ECS)
echo "Deploying to cloud..."

# Update ECS service (replace with your cluster and service names)
aws ecs update-service \
    --cluster business-ai-cluster \
    --service business-ai-service \
    --force-new-deployment

# Deploy Lambda functions
echo "Deploying Lambda functions..."

# Package handwriting recognition function
cd deployment/ai_models
zip -r handwriting-function.zip handwriting_model.py

# Deploy to AWS Lambda
aws lambda update-function-code \
    --function-name handwriting-recognition \
    --zip-file fileb://handwriting-function.zip

# Package invoice analyzer function
zip -r invoice-analyzer.zip invoice_analyzer.py

# Deploy to AWS Lambda
aws lambda update-function-code \
    --function-name invoice-analyzer \
    --zip-file fileb://invoice-analyzer.zip

echo "Deployment completed!"
echo "API endpoints:"
echo "- Handwriting Recognition: https://your-api-gateway.com/handwriting/recognize"
echo "- Invoice Analysis: https://your-api-gateway.com/invoice/analyze"
echo "- Translation: https://your-api-gateway.com/translate"