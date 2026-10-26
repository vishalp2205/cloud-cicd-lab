pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        AWS_REGION     = 'ap-south-1'
        AWS_ACCOUNT_ID = '340551173999'
        ECR_REPOSITORY = 'cca2-flask-app'
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_IMAGE      = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
        IMAGE_TAG      = "${BUILD_NUMBER}"
        APP_NAME       = 'flask-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh 'python3 -m pip install --user -r requirements.txt'
                sh 'python3 -m py_compile app.py'
                sh 'python3 -m unittest -v test_app.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${ECR_IMAGE}:${IMAGE_TAG} -t ${ECR_IMAGE}:latest .'
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    docker push ${ECR_IMAGE}:${IMAGE_TAG}
                    docker push ${ECR_IMAGE}:latest
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl create secret docker-registry ecr-secret \
                        --docker-server=${ECR_REGISTRY} \
                        --docker-username=AWS \
                        --docker-password="$(aws ecr get-login-password --region ${AWS_REGION})" \
                        --dry-run=client -o yaml | kubectl apply -f -
                    sed "s|IMAGE_PLACEHOLDER|${ECR_IMAGE}:${IMAGE_TAG}|" k8s/deployment.yaml | kubectl apply -f -
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/${APP_NAME} --timeout=180s
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    kubectl get pods -o wide
                    kubectl get deployment ${APP_NAME}
                    kubectl get svc flask-app-service
                    echo "Image in use:"
                    kubectl get deployment ${APP_NAME} -o jsonpath='{.spec.template.spec.containers[0].image}'
                    echo
                    echo "App response:"
                    curl -s http://$(minikube ip):30007
                    echo
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed - check the stage logs.'
        }
    }
}
