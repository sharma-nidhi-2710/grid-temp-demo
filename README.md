# Data Science Model Deployment Pipeline
This is a project for time-series prediction of the temperature of a transformer.
This project demonstrates how to select a pretrained model, run it locally, containerize it using Docker,
and deploy it to AWS using EC2, ECR, GitHub Actions, and S3.
## Project Overview
- Pretrained model selection and local testing
- Dockerized model inference application
- CI/CD deployment pipeline with GitHub Actions
- AWS setup using EC2, ECR, and S3
- Automated workflow triggered on repository updates
## 1. Select a Pretrained Model
We selected a pretrained model (e.g., HuggingFace Transformers). Model files downloaded:
- model.safetensors
- config.json
- generation_config.json
## 2. Run the Model Locally
```
python app.py
```
## 3. Save Model Weights Locally
Stored under `/model`.
## 4. Dockerize the Application
```
docker build -t mymodel-app .
docker run -p 8080:8080 mymodel-app
```
## 5. AWS Setup
Includes ECR repo, EC2 instance, self-hosted GitHub runner.
## 6. GitHub Actions CI/CD Pipeline
```
.github/workflows/deploy.yml
```
Automatically builds/pushes Docker image and deploys.
## 7. Upload Model Files to S3
Files uploaded:
- model.safetensors
- config.json
- generation_config.json
## Project Structure
project/
app.py
Dockerfile
requirements.txt
model/
.github/workflows/deploy.yml
## Deployment Flow Summary
1. Code pushed → GitHub
2. GitHub Actions builds Docker image
3. Image pushed to ECR
4. EC2 pulls latest image
5. App restarts and downloads model from S3
