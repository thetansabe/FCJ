# Local Kubernetes Lab Setup with Ingress Controller

This guide shows you how to set up a local Kubernetes cluster with an Ingress controller using Docker Desktop to simulate a production-like environment where multiple microservices share a single load balancer and use different domain names.

Prerequisites:

- Docker Desktop installed on Windows with WSL2 backend
- Settings > WSL Integration enabled for your Linux distro (remember to toggle on the Ubuntu distro)
- Kubernetes enabled in Docker Desktop settings (Kubeadm)

## Architecture

```
User Request
    |
    v
Load Balancer (ALB / NGINX Ingress Controller)
    |
    +---> app1.local ---> Ingress1 ---> Service1 ---> FastAPI App 1
    |
    +---> app2.local ---> Ingress2 ---> Service2 ---> FastAPI App 2

Ingresses with same `ingressClassName: nginx` are managed by the same NGINX Ingress Controller, which combines all rules into a single load balancer configuration.
```

## Step 1: Enable Kubernetes in Docker Desktop

1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (green icon in bottom-left)

## Step 2: Install NGINX Ingress Controller

```bash
# Install using kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Verify
kubectl get pods -n ingress-nginx
```

## Step 3: Create Local Kubernetes Manifests

Create `k8s/deployment-local.yaml`

Create `k8s/service.yaml`

Create `k8s/ingress-local.yaml`

See sample code

## Step 4: Build Docker Image

```bash
# Build your FastAPI app (Docker Desktop will have access)
docker build -t fastapi-app:latest .
```

## Step 5: Deploy the Application

```bash
# Apply manifests
kubectl apply -f k8s/deployment-local.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress-local.yaml

# Verify deployment
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

## Step 6: Configure Local DNS

Add to `C:\Windows\System32\drivers\etc\hosts` (run Notepad as Administrator):

```
# Added by Docker Desktop
192.168.100.149 host.docker.internal
192.168.100.149 gateway.docker.internal
# To allow the same kube context to work on the host and the container:
127.0.0.1 app1.local
127.0.0.1 app2.local
127.0.0.1 kubernetes.docker.internal # must have this entry for kubectl reach the cluster
```

## Multiple Microservices Example

### Create a Second Service

Create `app2` as example

Create `k8s` local files as example

Build second app image + run kubectl cmd like app1

Test both apps:

```bash
curl http://app1.local
curl http://app2.local
```

## Useful Commands

```bash
# Get all resources
kubectl get all

# Get pods with more details
kubectl get pods -o wide

# Check ingress details
kubectl describe ingress

# View pod logs
kubectl logs -l app=fastapi-app

# Port forward (alternative to ingress)
kubectl port-forward svc/fastapi-app-service 8000:80

# Delete all resources
kubectl delete -f k8s/
```

## Troubleshooting

### Ingress not working

```bash
# Check ingress controller status
kubectl get pods -n ingress-nginx

# Restart ingress controller if needed
kubectl rollout restart deployment -n ingress-nginx ingress-nginx-controller

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Can't access via hostname

- Verify hosts file entry in `C:\Windows\System32\drivers\etc\hosts`
- Try accessing via IP: `curl http://localhost`
- Check ingress rules: `kubectl describe ingress`

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Clean Up

```bash
# Delete all resources
kubectl delete -f k8s/

# Or disable Kubernetes in Docker Desktop Settings
```

## Advantages of This Setup

✅ **No Cloud Costs** - Everything runs locally  
✅ **No Minikube Needed** - Docker Desktop handles everything  
✅ **Fast Iteration** - No image push/pull delays  
✅ **Learn Kubernetes** - Same concepts as production  
✅ **Multiple Services** - Test microservices architecture  
✅ **Single Load Balancer** - One ingress controller for all apps

## Next Steps

1. Create a third microservice
2. Implement TLS with self-signed certificates
3. Try path-based routing (e.g., `app.local/api1`, `app.local/api2`)
4. Add ConfigMaps and Secrets
5. Practice rolling updates

## Resources

- [Docker Desktop Kubernetes](https://docs.docker.com/desktop/kubernetes/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
