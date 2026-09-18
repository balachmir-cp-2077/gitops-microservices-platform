# GitOps Microservices Platform

A production-grade GitOps delivery pipeline running on **Minikube** with **ArgoCD**, delivering a multi-service cloud-native application.

## Architecture

- **`order-service`**: Web front-end and order creation API. Connects to `inventory-service` over internal cluster DNS.
- **`inventory-service`**: Backend catalog and inventory management API.
- **Minikube**: Local Kubernetes engine.
- **ArgoCD**: GitOps continuous delivery controller reconciling desired Git state with live Kubernetes state.

## Project Structure

```text
gitops-microservices-platform/
├── services/
│   ├── inventory-service/     # Inventory microservice (FastAPI)
│   │   ├── app.py
│   │   └── requirements.txt
│   └── order-service/         # Order microservice (FastAPI + Web UI)
│       ├── app.py
│       └── requirements.txt
├── k8s/                       # Kubernetes manifests (Deployments, Services, ConfigMaps)
├── argocd/                    # ArgoCD Application CRDs
└── README.md
```
