# Pizza API - FastAPI with Kubernetes

A RESTful API for managing pizzas and ingredients, built with FastAPI and deployable to Kubernetes. This project demonstrates modern Python web development with containerization and orchestration.

## Features

- **Pizza Management**: Create, read, update, and delete pizzas with custom ingredients
- **Ingredient Management**: Manage a comprehensive ingredient database with allergen tracking
- **Advanced Search**: Search pizzas by name, description, and ingredients
- **Database Support**: PostgreSQL for production with SQLite fallback for development
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Kubernetes Ready**: Complete deployment manifests for container orchestration
- **Testing Suite**: Comprehensive test coverage for all endpoints

## Technology Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 13 (primary), SQLite (fallback)
- **ORM**: SQLAlchemy with Alembic migrations
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with Minikube support
- **Testing**: Pytest with FastAPI TestClient

## Virtual Environment setup

	mkvirtualenv venv -p python3
	workon venv
	pip install -r requirements.txt
	uvicorn app.main:app --reload

FastAPI HTTP server starts on port 8000.

## Kubernetes Setup

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed and running
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- Docker installed

### Setup Instructions

1. **Start Minikube cluster**:
   ```bash
   minikube start
   ```

2. **Configure Docker environment to use Minikube's Docker daemon**:
   ```bash
   eval $(minikube docker-env)
   ```

3. **Build the application Docker image**:
   ```bash
   docker build -t pizza-api:local .
   ```

4. **Deploy PostgreSQL database**:
   ```bash
   kubectl apply -f postgres-deployment.yaml
   kubectl apply -f postgres-service.yaml
   ```

5. **Wait for PostgreSQL to be ready**:
   ```bash
   kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
   ```

6. **Deploy the Pizza API application**:
   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

7. **Wait for the application to be ready**:
   ```bash
   kubectl wait --for=condition=ready pod -l app=pizza-api --timeout=300s
   ```

8. **Access the application**:
   ```bash
   # Get the service URL
   minikube service pizza-api-service --url
   
   # Or use port forwarding
   kubectl port-forward svc/pizza-api-service 8080:80
   ```

### Testing the API

Once the service is running, you can test the API:

```bash
# Health check
curl http://localhost:8080/

# API documentation
curl http://localhost:8080/docs

# Health checker endpoints
curl http://localhost:8080/api/healthchecker
curl http://localhost:8080/api/db-healthchecker
```

### Useful Commands

```bash
# Check pod status
kubectl get pods

# View application logs
kubectl logs -l app=pizza-api

# View PostgreSQL logs
kubectl logs -l app=postgres

# Delete all resources
kubectl delete -f deployment.yaml
kubectl delete -f service.yaml
kubectl delete -f postgres-deployment.yaml
kubectl delete -f postgres-service.yaml
```

### Troubleshooting

- **ImagePullBackOff**: Make sure you've run `eval $(minikube docker-env)` before building the Docker image
- **Database connection issues**: Ensure PostgreSQL pod is running with `kubectl get pods -l app=postgres`
- **Service not accessible**: Use `minikube service pizza-api-service --url` to get the correct URL

