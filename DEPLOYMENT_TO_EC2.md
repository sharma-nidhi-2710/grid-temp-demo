# ☁️ Single-Instance CI/CD

This document details the first phase of deployment, leveraging a self-hosted **GitHub Actions Runner** on an **AWS EC2** instance to create a continuous delivery pipeline.
---

### 1. Environment Setup

An EC2 instance (Ubuntu/Amazon Linux) was provisioned to serve as the application host and the **self-hosted GitHub Actions runner**.

#### 1.1. Installing Docker

Docker was installed on the EC2 instance to run the containerized application.

* **Command Output:**
    ```bash
    ubuntulip-172-31-21-31:-/actione runner sudo apt-get install -y docker.io
    [... package lists and dependencies ...]
    Fetched 76.0 M in 19S. Ma
    ```
    <img width="1508" height="374" alt="image" src="https://github.com/user-attachments/assets/b39ca590-029b-4ba7-acde-157993994df0" />
    <img width="1512" height="346" alt="image" src="https://github.com/user-attachments/assets/82bef7ae-05f9-40be-b2c9-b2fa1ce84b0c" />

#### 1.2. Configuring the GitHub Actions Runner

The runner was configured to connect to the repository to listen for jobs.

* **Commands (Abstracted):**
    ```bash
    # Update and install dependencies
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl jq git docker.io

    # Setup runner directory
    mkdir actions-runner && cd actions-runner
    curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://...
    tar xzf actions-runner-linux-x64-2.329.0.tar.gz

    # Configure runner (using repository URL and token)
    ./config.sh --url https://github.com/sharma-nidhi-2710/grid-temp-demo --token ***
    ```
* **Runner Running:**
    ```bash
    2025-12-06 10:23:522: Listening for Jobs
    ```
    <img width="1512" height="457" alt="image" src="https://github.com/user-attachments/assets/e42d0c16-881d-43a7-aa06-3af8404faa3d" />


### 2. ECR and S3 Integration

#### 2.1. ECR Repository

The container image for the application was built and pushed to **AWS ECR (Elastic Container Registry)**.

* **ECR Details:**
    * **Repository:** `grid-demo`
    * **Image Tag:** `sha256:d1d33ba...`
<img width="1507" height="446" alt="image" src="https://github.com/user-attachments/assets/fa8e2ab1-eeb3-4fe3-829b-2b4bf8864ac4" />

#### 2.2. Decoupling Model Weights using S3

The model weights were stored in an **AWS S3 bucket** (`s3://grid-demo-ns/`) and pulled at the start of the deployment.

* **Model Pulling Command:**
    ```bash
    aws s3 cp s3://grid-demo-ns/model.safetensors ./model
    ```
    ---

### 3. CI/CD Execution and Testing

The GitHub Action automatically executed the deployment, which included pulling the S3 model and running the Docker container.

* **Container Status:**
    ```bash
    ubuntu@ip-172-31-21-31:~/actions-runner$ docker ps
    CONTAINER ID        IMAGE                                                                               COMMAND
    b242e               720744104786.dkr.ecr.us-east-1.amazonaws.com/grid-demo:latest "/uvicorn app:app ..."
    STATUS              PORTS
    Up About a minute (healthy) 0.0.0.0:8000->8000/tcp, 78000->8000/tcp
    ```
    * **Local Test Request:** A `curl` request was made to the hosted application endpoint on the EC2 instance.
    ```bash
    ubuntu@ip-172-31-21-31:~/actions-runner$ curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"historical_temps": [20, 21, 22, 23, 24], "prediction_length": 24}'
    ```
    <img width="1505" height="541" alt="image" src="https://github.com/user-attachments/assets/2d346e75-0f16-4af3-a76e-0c88f570b7a0" />

    * **Result:** The API returned the prediction data, confirming the application was running locally in the container and serving the model.
### 4. Demo Video: https://drive.google.com/file/d/1ruQYYPQm08J_AHUMe0dDkkPGNTP3AUW3/view?usp=drive_link
