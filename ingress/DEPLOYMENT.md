# Deploying FastAPI App to EKS with Ingress Controller

This guide walks you through deploying the FastAPI application to Amazon EKS with an Application Load Balancer (ALB) Ingress Controller.

## Prerequisites

- AWS CLI installed and configured
- kubectl installed
- eksctl installed (recommended for EKS cluster creation)
- Docker installed
- Docker Hub account
- An AWS account with appropriate permissions

## Step 1: Create an EKS Cluster

If you don't have an EKS cluster yet, create one:

```bash
eksctl create cluster \
  --name my-fastapi-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

Configure kubectl to use your cluster:

```bash
aws eks update-kubeconfig --name my-fastapi-cluster --region us-east-1
```

Verify connection:

```bash
kubectl get nodes
```

## Step 2: Build and Push Docker Image to Docker Hub

### Option A: Using PowerShell Script (Recommended for Windows)

Run the build and push script:

```powershell
.\build-and-push.ps1 -DockerHubUsername <YOUR_DOCKERHUB_USERNAME>
```

Optional parameters:

- `-ImageName`: Custom image name (default: "fastapi-app")
- `-ImageTag`: Image tag (default: "latest")

Example with custom parameters:

```powershell
.\build-and-push.ps1 -DockerHubUsername myusername -ImageName my-fastapi-app -ImageTag v1.0.0
```

### Option B: Manual Steps

Login to Docker Hub:

```bash
docker login -u <YOUR_DOCKERHUB_USERNAME>
```

Build the Docker image:

```bash
docker build -t fastapi-app .
```

Tag the image:

```bash
docker tag fastapi-app:latest <YOUR_DOCKERHUB_USERNAME>/fastapi-app:latest
```

Push to Docker Hub:

```bash
docker push <YOUR_DOCKERHUB_USERNAME>/fastapi-app:latest
```

## Step 3: Install AWS Load Balancer Controller

### 3.1: Create IAM OIDC Provider

```bash
eksctl utils associate-iam-oidc-provider \
  --region us-east-1 \
  --cluster my-fastapi-cluster \
  --approve
```

### 3.2: Download IAM Policy

```bash
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.0/docs/install/iam_policy.json
```

### 3.3: Create IAM Policy

```bash
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam-policy.json
```

### 3.4: Create IAM Service Account

```bash
eksctl create iamserviceaccount \
  --cluster=my-fastapi-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --region us-east-1 \
  --approve
```

### 3.5: Install AWS Load Balancer Controller using Helm

Add the EKS chart repository:

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
```

Install the controller:

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=my-fastapi-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

Verify installation:

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```

## Step 4: Update Deployment Manifest

Edit `k8s/deployment.yaml` and replace `<YOUR_DOCKERHUB_USERNAME>` with your actual Docker Hub username:

```yaml
image: <YOUR_DOCKERHUB_USERNAME>/fastapi-app:latest
```

For example:

```yaml
image: johndoe/fastapi-app:latest
```

## Step 5: Deploy the Application

### Option A: Using PowerShell Script (Recommended)

```powershell
.\deploy.ps1
```

### Option B: Manual Deployment

Apply all Kubernetes manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## Step 6: Verify Deployment

Check deployment status:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

Wait for the ALB to be provisioned (this may take 2-3 minutes):

```bash
kubectl get ingress fastapi-app-ingress -w
```

## Step 7: Access Your Application

Get the ALB URL:

```bash
kubectl get ingress fastapi-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Test the application:

```bash
curl http://<ALB_URL>/
```

You should see: `{"message":"Hello World"}`

## Optional: Enable HTTPS

To enable HTTPS with an SSL certificate:

1. Request or import a certificate in AWS Certificate Manager (ACM)
2. Update `k8s/ingress.yaml` with the certificate ARN (uncomment the HTTPS annotations)
3. Reapply the ingress:

```bash
kubectl apply -f k8s/ingress.yaml
```

## Troubleshooting

### Check Pod Logs

```bash
kubectl logs -l app=fastapi-app
```

### Check Ingress Controller Logs

```bash
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### Describe Ingress

```bash
kubectl describe ingress fastapi-app-ingress
```

### Check ALB in AWS Console

- Go to EC2 > Load Balancers
- Find the ALB created by the ingress controller
- Check target groups and health checks

## Cleanup

To delete all resources:

```bash
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
```

To delete the EKS cluster:

```bash
eksctl delete cluster --name my-fastapi-cluster --region us-east-1
```

## Architecture

```
Internet
    |
    v
Application Load Balancer (ALB)
    |
    v
Ingress Controller
    |
    v
Service (NodePort)
    |
    v
Deployment (2 replicas)
    |
    v
Pods (FastAPI containers)
```

## Additional Resources

- [AWS Load Balancer Controller Documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
