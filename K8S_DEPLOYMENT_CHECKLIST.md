# Kubernetes Deployment Checklist

Complete these steps in order to deploy your Grid Temperature Forecasting model to Kubernetes.

## Prerequisites (Before Starting)
- [ ] AWS Account with appropriate permissions
- [ ] `kubectl` installed (`brew install kubectl` or download from kubernetes.io)
- [ ] AWS CLI v2 installed and configured
- [ ] `eksctl` installed (`brew install eksctl` on macOS)
- [ ] Docker installed (you already have this)
- [ ] Your model image already pushed to ECR (`grid-demo:latest`)

### Verify Prerequisites
```bash
kubectl version --client
aws --version
eksctl version
docker --version
```

---

## Phase 1: Create Kubernetes Cluster (20-30 minutes)

### Option 1: Using eksctl (Recommended - Easiest)
- [ ] Run the eksctl command to create cluster:
```bash
eksctl create cluster \
  --name grid-demo-cluster \
  --version 1.28 \
  --region us-east-1 \
  --nodegroup-name grid-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 5
```
- [ ] Wait for cluster creation (15-20 minutes)
- [ ] Verify cluster was created:
```bash
eksctl get clusters
```

### Option 2: Using AWS Console
- [ ] Go to AWS Console → EKS → Clusters
- [ ] Click "Create cluster"
- [ ] Fill in:
  - [ ] Cluster name: `grid-demo-cluster`
  - [ ] Kubernetes version: 1.28 (or latest)
  - [ ] Service role: Create new or select existing
  - [ ] VPC: Select your VPC
  - [ ] Subnets: Select at least 2 subnets in different AZs
  - [ ] Security group: Select or create
- [ ] Click "Create"
- [ ] Wait for cluster status to be "ACTIVE"
- [ ] Add node group:
  - [ ] Subnets: Select 2+ subnets
  - [ ] Instance type: t3.medium
  - [ ] Desired size: 2

---

## Phase 2: Connect kubectl to Cluster (5 minutes)

- [ ] Update kubeconfig:
```bash
aws eks update-kubeconfig \
  --name grid-demo-cluster \
  --region us-east-1
```

- [ ] Verify connection:
```bash
kubectl cluster-info
```

- [ ] Check nodes are ready:
```bash
kubectl get nodes
# Should show 2 nodes with status "Ready"
```

---

## Phase 3: Configure AWS Access for Pods (10 minutes)

- [ ] Create IAM policy for S3 access:
```bash
cat > s3-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::grid-demo-ns",
                "arn:aws:s3:::grid-demo-ns/*"
            ]
        }
    ]
}
EOF
```

- [ ] Create the policy:
```bash
aws iam create-policy \
  --policy-name GridDemoS3Access \
  --policy-document file://s3-policy.json
```

- [ ] Create ServiceAccount with IAM role:
```bash
eksctl create iamserviceaccount \
  --name grid-demo-sa \
  --namespace default \
  --cluster grid-demo-cluster \
  --attach-policy-arn arn:aws:iam::720744104786:policy/GridDemoS3Access \
  --approve
```

- [ ] Verify ServiceAccount created:
```bash
kubectl get serviceaccount grid-demo-sa
```

---

## Phase 4: Prepare Deployment Configuration (5 minutes)

- [ ] Edit `k8s/deployment.yaml`:
```bash
# Replace these placeholders with your values:
# <AWS_ACCOUNT_ID> → 720744104786
# <REGION> → us-east-1
# <ECR_REPOSITORY_NAME> → grid-demo

# Or use sed to replace:
sed -i 's/<AWS_ACCOUNT_ID>/720744104786/g' k8s/deployment.yaml
sed -i 's/<REGION>/us-east-1/g' k8s/deployment.yaml
sed -i 's/<ECR_REPOSITORY_NAME>/grid-demo/g' k8s/deployment.yaml
```

- [ ] Verify the image URI looks correct:
```bash
grep "image:" k8s/deployment.yaml
# Should be: 720744104786.dkr.ecr.us-east-1.amazonaws.com/grid-demo:latest
```

- [ ] Verify image exists in ECR:
```bash
aws ecr describe-images \
  --repository-name grid-demo \
  --region us-east-1
```

---

## Phase 5: Deploy to Kubernetes (5 minutes)

- [ ] Apply the deployment:
```bash
kubectl apply -f k8s/deployment.yaml
```

- [ ] Check deployment status:
```bash
kubectl get deployment grid-temp-forecasting
```

- [ ] Check if pods are running:
```bash
kubectl get pods
# Should show 2 pods with "Running" status
```

- [ ] Wait for pods to be ready (may take 1-3 minutes):
```bash
kubectl rollout status deployment/grid-temp-forecasting
```

- [ ] View logs to verify app started:
```bash
kubectl logs -l app=grid-temp-forecasting --tail=50
# Should show "INFO: Uvicorn running on" message
```

---

## Phase 6: Access Your Application (5 minutes)

- [ ] Get the external LoadBalancer IP:
```bash
kubectl get svc grid-temp-forecasting-service
# Wait for EXTERNAL-IP column to have an IP address
# This can take 1-2 minutes
```

- [ ] Test the health endpoint:
```bash
# Replace with your external IP
curl http://<EXTERNAL-IP>/health
# Should return: {"status":"healthy"}
```

- [ ] Access the Swagger UI in browser:
```
http://<EXTERNAL-IP>/docs
```

- [ ] Test with a prediction (via curl):
```bash
curl -X POST http://<EXTERNAL-IP>/predict \
  -H "Content-Type: application/json" \
  -d '{"historical_temps": [20, 21, 22, 23, 24], "prediction_length": 24}'
```

---

## Phase 7: Verify Monitoring and Scaling (10 minutes)

- [ ] Check HPA (Auto-scaling) status:
```bash
kubectl get hpa
kubectl describe hpa grid-temp-forecasting-hpa
```

- [ ] Monitor pod resource usage:
```bash
kubectl top pods
```

- [ ] Check all resources are running:
```bash
kubectl get all
# Should show:
# - Deployment: grid-temp-forecasting
# - ReplicaSet: grid-temp-forecasting-xxxxx
# - Pods: 2 running
# - Service: grid-temp-forecasting-service with external IP
# - HPA: grid-temp-forecasting-hpa
```

---

## Phase 8: Post-Deployment Verification (Ongoing)

- [ ] View real-time logs:
```bash
kubectl logs -f deployment/grid-temp-forecasting
```

- [ ] Monitor for errors:
```bash
kubectl get events --sort-by='.lastTimestamp'
```

- [ ] Check pod health:
```bash
kubectl describe pod <pod-name>
# Look for: "Running" status and "Ready" condition = True
```

---

## Optional: Advanced Configuration

- [ ] Update GitHub Actions to deploy to K8s instead of EC2:
  - [ ] Add kubectl configuration to CI/CD pipeline
  - [ ] Update deployment step to use `kubectl apply`

- [ ] Set up monitoring:
  - [ ] Install Prometheus
  - [ ] Install Grafana
  - [ ] Create dashboards

- [ ] Set up ingress controller:
  - [ ] Install AWS Application Load Balancer Controller
  - [ ] Create Ingress resource for custom domain

- [ ] Set up logging:
  - [ ] Configure CloudWatch Container Insights
  - [ ] Set up log aggregation

---

## Troubleshooting Checklist

### Pods not running?
- [ ] Check pod status: `kubectl describe pod <pod-name>`
- [ ] View logs: `kubectl logs <pod-name>`
- [ ] Common causes:
  - [ ] Image pull failure: Verify ECR image URI
  - [ ] OOMKilled: Increase memory limits
  - [ ] Pending: Check node resources: `kubectl top nodes`

### Can't reach application?
- [ ] Verify service has external IP: `kubectl get svc`
- [ ] Verify pods are running: `kubectl get pods`
- [ ] Verify security groups allow port 80
- [ ] Try port forward: `kubectl port-forward svc/grid-temp-forecasting-service 8000:80`

### Deployment stuck?
- [ ] Check deployment events: `kubectl describe deployment grid-temp-forecasting`
- [ ] Check for image pull issues: `kubectl describe pod <pod-name>`
- [ ] Try restarting: `kubectl rollout restart deployment/grid-temp-forecasting`

---

## Cleanup Checklist (When Done)

- [ ] Delete Kubernetes resources:
```bash
kubectl delete -f k8s/deployment.yaml
```

- [ ] Delete cluster (if using eksctl):
```bash
eksctl delete cluster --name grid-demo-cluster
```

- [ ] Delete EC2 resources created by eksctl:
- [ ] Delete security groups
- [ ] Delete VPC (if you created a new one)
- [ ] Verify in AWS Console everything is deleted

---

## Files Used

- `k8s/deployment.yaml` - Main deployment configuration
- `KUBERNETES_DEPLOYMENT.md` - Detailed guide
- `K8S_QUICK_REFERENCE.md` - Command reference

## Support Commands

```bash
# Get help
kubectl --help
kubectl explain deployment
kubectl explain pod

# Get cluster info
kubectl cluster-info
kubectl get apiresources

# Debug a pod
kubectl exec -it <pod-name> -- /bin/bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

---

## Success Criteria

✅ You have successfully deployed to Kubernetes when:
- [ ] EKS cluster is running with 2 nodes
- [ ] kubectl connects to the cluster
- [ ] 2 pods are running the grid-demo application
- [ ] Service has an external LoadBalancer IP
- [ ] Can access `/health` endpoint via external IP
- [ ] Can access `/docs` Swagger UI in browser
- [ ] HPA is monitoring and ready to scale
