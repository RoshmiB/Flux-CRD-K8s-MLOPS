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






Step 1 — Start cluster
minikube start
Step 2 — Build & push Docker image
docker build -t YOUR_DOCKERHUB/ml-api:latest ./app
docker push YOUR_DOCKERHUB/ml-api:latest

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