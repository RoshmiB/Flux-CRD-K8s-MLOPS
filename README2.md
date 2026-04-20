# 🚀 ML GitOps Deployment using FluxCD

This project demonstrates how to deploy a Machine Learning model using GitOps principles with FluxCD and Kubernetes.

## 🧩 Architecture

- FastAPI ML model
- Docker containerization
- Kubernetes deployment
- GitOps using FluxCD

## ⚙️ Workflow

1. Code pushed to GitHub
2. FluxCD watches repository
3. Automatically applies Kubernetes manifests
4. Deploys ML API to cluster

## 🔥 Features

- Automated deployments via GitOps
- Scalable Kubernetes setup
- Simple ML model serving API

## 🧪 API

### Predict:
GET /predict?x=5


## 📌 Future Improvements

- Add CI/CD pipeline
- Add monitoring (Prometheus)
- Add model versioning

Steps:- 
create one python venv first:-
1. source source /Users/rajaguru/Documents/interview_prep/Flux-CRD-K8s/.venv/bin/activate
2. pip install -r  requirements.txt
3. deactivate (to come out of venv)
4. python train.py
Output:
model.pkl
5. uvicorn app:app --reload

![alt text](image-1.png)

6. 👉 Open browser:
http://127.0.0.1:8000/docs
You’ll see Swagger UI

![alt text](image-2.png)

7. Example input 
{
  "MedInc": 8.3,
  "HouseAge": 40,
  "AveRooms": 6,
  "Population": 300,
  "AveOccup": 3,
  "Latitude": 37.8,
  "Longitude": -122.2
}

output :-

![alt text](image-3.png)

7. cd app
docker build -t ml-app .

![alt text](image-4.png)

8. docker run -p 8000:8000 ml-app

9. 
Build & push Docker image

aws ecr create-repository --repository-name ml-app

Login
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 725490567891.dkr.ecr.us-west-2.amazonaws.com
Login Succeeded

cat ~/.docker/config.json 
{
        "auths": {
                "725490567891.dkr.ecr.us-west-2.amazonaws.com": {},
                "aksdemosampleroshmi.azurecr.io": {},
                "https://index.docker.io/v1/": {},
                "public.ecr.aws": {}
        },
        "credsStore": "desktop"
}%                                              


docker tag ml-app:latest 725490567891.dkr.ecr.us-west-2.amazonaws.com/ml-app:v1
docker push 725490567891.dkr.ecr.us-west-2.amazonaws.com/ml-app:v1


10. 
Create cluster :-
`
eksctl create cluster \
  --name ml-cluster \
  --region us-west-2 \
  --nodegroup-name ml-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed

Add EBS CSI addon :-
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster ml-cluster \
  --region us-west-2

Install AWS Load Balancer Controller
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

eksctl create iamserviceaccount \
  --cluster=ml-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::725490567891:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=ml-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

kubectl get pods -n kube-system
`




👉 Replace in deployment.yaml

Step 3 — Install Flux
flux install
Step 4 — Connect repo to cluster
flux bootstrap github \
  --owner=YOUR_USERNAME \
  --repository=ml-gitops-flux-demo \  
  --branch=main \
  --path=./clusters/dev \
  --personal
Step 5 — Verify deployment
kubectl get pods
kubectl get svc
Step 6 — Access app
minikube service ml-api

11. Flux video :- 
    https://www.youtube.com/watch?v=DqXDrAR4cJ4