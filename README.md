# CCA 2 - CI/CD Pipeline for a Flask Application

Automated delivery of a small Flask web application:
**GitHub -> Jenkins -> Docker -> AWS ECR -> Minikube (Kubernetes)**, all running on an AWS EC2 server.

## 1. Project chosen

A small Flask web application built earlier for CCD Assignment 5. It serves one web page.
The guide marks the pipeline, not the application, so this existing project was reused.

- Version 1: plain text page ("Version 1 - CCA 2 CI/CD Pipeline")
- Version 2 (the second-run change): styled page with a version badge and the name of the pod that served the request

## 2. Repository structure

Files in the repository:

    cloud-cicd-lab/
    |-- app.py                Flask application
    |-- test_app.py           Unit test (home page returns HTTP 200)
    |-- requirements.txt      Python dependencies
    |-- Dockerfile            Container image definition
    |-- Jenkinsfile           Declarative pipeline
    |-- k8s/
    |   |-- deployment.yaml   Kubernetes Deployment (2 replicas)
    |   |-- service.yaml      Kubernetes Service (NodePort 30007)
    |-- README.md

## 3. Pipeline stages

Jenkins checks GitHub about every 2 minutes (pollSCM), so a push starts the pipeline automatically.

| Stage | What it does |
|---|---|
| Source code | Code, Dockerfile, Jenkinsfile and k8s files are stored in this GitHub repository |
| Checkout | Jenkins pulls the latest code from the main branch |
| Build and Test | Installs dependencies, syntax-checks app.py with py_compile, runs the unit test |
| Docker Build | Builds the image from the Dockerfile, tagged with the build number and latest |
| Push Image | Logs in to AWS ECR and pushes both tags |
| Deploy to Minikube | Refreshes the registry secret, puts the new image tag into the Deployment, applies the Deployment and Service, waits for the rollout |
| Verify | Lists pods, deployment and service, prints the image in use, requests the app page |

## 4. How Jenkins was set up on AWS

- EC2 instance: Amazon Linux 2023, c7i-flex.large, 30 GiB disk, region ap-south-1 (Mumbai)
- Security group: SSH (22) and Jenkins (8080) allowed only from the administrator IP address
- IAM role jenkins-ec2-ecr-role (policy AmazonEC2ContainerRegistryPowerUser) attached to the instance, so no access keys are stored anywhere
- Installed: Git, Docker, Java 21 (Amazon Corretto), Python 3, Jenkins 2.580.1, kubectl, Minikube
- The jenkins user was added to the docker group, and Minikube was started as the jenkins user, so pipeline steps can run docker and kubectl
- A 2 GB swap file was added as memory headroom
- Jenkins plugins: suggested plugins (Git, Pipeline)
- Job: cca2-pipeline, type Pipeline, "Pipeline script from SCM", Git, branch */main, script path Jenkinsfile

## 5. How the image was pushed

- Registry: private AWS ECR repository cca2-flask-app in ap-south-1
- Authentication: aws ecr get-login-password | docker login, using the temporary credentials of the instance IAM role
- Tags: the Jenkins build number (traceable, allows rollback) and latest

## 6. How the app was deployed and accessed

- k8s/deployment.yaml runs 2 replicas; its image field holds IMAGE_PLACEHOLDER, which the pipeline replaces with the exact ECR image and tag using sed
- k8s/service.yaml exposes the pods as a NodePort service on port 30007
- ECR is private and ECR login tokens expire after 12 hours, so the pipeline recreates the ecr-secret image pull secret on every run
- kubectl rollout status makes the pipeline fail if the new pods do not become ready
- The Minikube node address is only reachable from the server, so the app is checked with curl on the server and opened from a laptop through an SSH tunnel

SSH tunnel command:

    ssh -L 8081:<minikube-ip>:30007 -i <key>.pem ec2-user@<server-public-ip>

Then browse to http://localhost:8081

## 7. Second run (code change)

- app.py was changed from the plain text page to the styled Version 2 page and pushed to main
- Jenkins detected the new commit by itself ("Started by an SCM change") and ran build #2
- A new image with tag 2 was pushed to ECR, and Kubernetes performed a rolling update to the new pods
- The browser then showed Version 2 and the pod name

## 8. Run locally

Commands:

    pip install -r requirements.txt
    python -m unittest -v test_app.py
    python app.py
