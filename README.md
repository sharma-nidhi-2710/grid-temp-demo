# 🚀 Grid Temperature Forecasting API

This repository hosts the backend service for a **Grid Temperature Forecasting API**. The service is built with **FastAPI/Uvicorn**, uses a pre-trained **ML model** provided by the AI engineering team to predict grid temperatures, and demonstrates a robust, modern deployment pipeline across different cloud platforms.

https://github.com/user-attachments/assets/f902c698-35ec-45e4-8637-d6a9acf8fbca

### 🔑 Key Project Learnings

* **Full Deployment Lifecycle:** Demonstrated end-to-end deployment, starting from local development, containerization, and deployment to EC2, culminating in a highly available, scalable **Amazon EKS (Kubernetes)** cluster.
* **Infrastructure as Code (IaC) Principles:** Managed CI/CD pipelines using **GitHub Actions** and container orchestration.
* **Decoupling Workload:** Implemented **AWS S3** for storing large model weights, decoupling the model from the application logic for efficient deployment and versioning.
* **Cloud Observability:** Configured and monitored application health and performance using **AWS CloudWatch** and **Container Insights**.

---

### 🛠️ Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn | API development and serving the prediction model. |
| **Model Storage** | AWS S3 | Secure, scalable storage for the large model weights (`model.safetensors`). |
| **Containerization** | Docker, AWS ECR | Packaging the application and hosting the immutable container image. |
| **CI/CD** | GitHub Actions | Automated build, tag, and push to ECR, and deployment to EC2. |
| **Deployment Platforms** | AWS EC2, AWS EKS (Kubernetes) | Hosting environments for the application. |
| **Orchestration** | Karpenter | Dynamic, cost-optimized Kubernetes node provisioning. |
| **Networking** | AWS ELB (Load Balancer) | Providing a stable, external endpoint and high availability. |
| **Observability** | AWS CloudWatch, Container Insights | Centralized logging, metrics, and cluster health monitoring. |

---

### 🗺️ Deployment Deep Dives

This project includes detailed documentation and video demonstrations on the two distinct deployment stages:

| Deployment Stage | Description | Key Focus | Video Demo |
| :--- | :--- | :--- | :--- |
| **[EC2 Deployment](./DEPLOYMENT_TO_EC2.md)** | Initial deployment to a single EC2 instance using a self-hosted GitHub Actions runner. | CI/CD pipeline, Docker, and S3 integration. | [Link to EC2 Video Demo] |
| **[Kubernetes Deployment](./DEPLOYMENT_TO_KUBERNETES.md)** | Transition to a fully managed, scalable EKS cluster. | EKS cluster setup, IAM roles/Service Accounts, and observability. | [Link to K8s Video Demo] |

---

### 📞 API Endpoints

The deployed application provides the following endpoints, which can be accessed via the Load Balancer DNS (for the Kubernetes deployment) or the EC2 public IP (for the EC2 deployment).

| Endpoint | Method | Description | Example Request Body |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | Health check for the service. | N/A |
| `/predict` | `POST` | Accepts historical temps and returns a 24-hour forecast. | `{"historical_temps": [20, 21, 22, 23, 24], "prediction_length": 24}` |

**API Documentation (Swagger UI)**
