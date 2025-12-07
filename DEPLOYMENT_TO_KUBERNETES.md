# 🚢 Scalable EKS Cluster

This document details the transition to a scalable, highly available architecture using **AWS Elastic Kubernetes Service (EKS)**.

---

### 1. EKS Cluster Configuration

The EKS cluster (`grid-demo-cluster`) was configured using the AWS Console.

* **Kubernetes Version:** 1.34.
* **IAM Roles:** Dedicated roles were created for the Cluster and Nodes.
* [cite_start]**VPC and Subnets:** The cluster was deployed across multiple subnets [cite: 128, 139-146].

**Cluster Configuration:**
<img width="1144" height="647" alt="image" src="https://github.com/user-attachments/assets/c7a12bea-7726-4f04-abc2-6a5b7bcacd17" />
<img width="1138" height="846" alt="image" src="https://github.com/user-attachments/assets/6fda8cb4-21e2-4e14-805a-86c6d0d6ecd8" />

### 2. Node and Scaling Strategy

The project utilized a mix of node management strategies, with a preference for **Karpenter** for dynamic resource efficiency.

* **Deployment:** The deployment used a **Deployment** resource with **2 replicas** and was backed by a **Horizontal Pod Autoscaler (HPA)**.
    * `minReplicas`: 2.
    * `maxReplicas`: 10.
    * **Scaling Trigger:** CPU utilization $> 70\%$ or Memory utilization $> 80\%$.
* **Karpenter-Managed Nodes:** The application pods were running on a Karpenter-managed node, which automatically provisions the right-sized, cost-optimized instances (e.g., `c6a.xlarge`) based on actual pod demand.

| Feature | AWS Managed Node Group (MNG) | **Karpenter-Managed** |
| :--- | :--- | :--- |
| **Scaling** | AWS (via ASG) | **Karpenter (dynamic)** |
| **Optimization** | Based on config | **Based on actual pod demand** |
| **Example** | `grid-demo-node-group` | `i-0cb7622821786a9fa` |

### 3. Troubleshooting and Resolutions

Two significant issues were encountered and resolved, demonstrating core Kubernetes and AWS networking troubleshooting skills:

#### 3.1. ECR Pull Permissions Fix: `ImagePullBackOff`

* **Root Cause:** The Node IAM role (`grid-demo-new`) was missing the required ECR read policy.
* **Solution:** Attached the **`AmazonEC2ContainerRegistryReadOnly`** policy to the node role.
* **Result:** Pods were able to successfully pull the image, becoming **Running and Ready (1/1)**.
  <img width="1143" height="573" alt="image" src="https://github.com/user-attachments/assets/abc8b6de-9a0a-432c-a461-7393782cd84e" />

#### 3.2. Load Balancer Fix: `<pending>` Service

* [cite_start]**Root Cause:** The AWS Load Balancer Controller could not provision the ELB due to missing **VPC Subnet Tags** and a missing **Service Annotation** [cite: 549-551].
* **Solution:**
    * Tagged subnets with `kubernetes.io/role/elb=1` and `kubernetes.io/cluster/grid-demo-cluster=shared`.
    * Added `service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"` annotation to the Service manifest.
* **Result:** Load Balancer provisioned successfully, providing an **External DNS**.

### 4. Application Access

The application is accessed via the provisioned **External Load Balancer** DNS.

* **Load Balancer Type:** External Load Balancer (ELB).
* **External DNS:** `http://k8s-default-gridtemp-7355805242-82111ae4d33da55d.elb.us-east-1.amazonaws.com`.
  <img width="1118" height="639" alt="image" src="https://github.com/user-attachments/assets/b4af2d0d-83b2-4df1-9363-372fcf9642b2" />
* **Example Request (Curl):**
    ```bash
    curl -X POST http://k8s-default-gridtemp-7355805242-82111ae4d33da55d.elb.us-east-1.amazonaws.com/predict\
    -H "Content-Type: application/json" -d '{"historical_temps": [20, 21, 22, 23, 24], "prediction_length": 24}'
    ```

### 5. Observability with CloudWatch Container Insights

**CloudWatch Container Insights** was used to monitor the EKS cluster and collect logs.

* **Dashboard:**
* **Logs Resolution:** Initial log writing failed due to the node IAM role (`grid-demo-new`) lacking permissions for CloudWatch Logs.
    * **Fix:** An IAM policy granting CloudWatch permissions (`logs:PutLogEvents`, `logs:CreateLogStream`, etc.) was attached to the node IAM role.
    * **Result:** Logs are now actively being written to the centralized log groups.
* **Log Groups:** Application logs are written to `/aws/containerinsights/grid-demo-cluster/application`.
    * **CloudWatch Log Groups Screenshot:**
    <img width="1182" height="764" alt="image" src="https://github.com/user-attachments/assets/3c68d1c8-7fc6-4f8e-b2a0-53849f874966" />
* **Log Content:** The application logs currently show routine **Load Balancer Health Checks** (from the ELB) logs every $\sim \mathbf{10}$ seconds, confirming the service is healthy.
* **CloudWatch Insights:** Used for efficiently querying and analyzing log streams using a SQL-like language.
    <img width="1109" height="581" alt="image" src="https://github.com/user-attachments/assets/469364d2-b829-46d5-add2-b27bb834035c" />
