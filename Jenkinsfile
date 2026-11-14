pipeline {
  agent any

  environment {
    IMAGE  = "pranav4dit/todo-app"
    APP_IP = "54.79.90.229"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build') {
      steps { sh 'docker build -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .' }
    }

    stage('Test') {
      steps { sh 'docker run --rm $IMAGE:$BUILD_NUMBER python -m pytest -q' }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
            usernameVariable: 'U', passwordVariable: 'P')]) {
          sh '''
            echo "$P" | docker login -u "$U" --password-stdin
            docker push $IMAGE:$BUILD_NUMBER
            docker push $IMAGE:latest
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        sshagent(['ec2-key']) {
          sh '''
            ssh -o StrictHostKeyChecking=no ec2-user@$APP_IP "
              docker pull $IMAGE:$BUILD_NUMBER &&
              docker rm -f todo || true &&
              docker run -d --name todo --restart unless-stopped -p 80:5000 $IMAGE:$BUILD_NUMBER"
          '''
        }
      }
    }

    stage('Verify') {
      steps { sh 'sleep 5 && curl -f http://$APP_IP/health' }
    }
  }

  post {
    always  { sh 'docker logout || true' }
    success { echo "Deployed build ${BUILD_NUMBER} to http://${APP_IP}" }
    failure { echo "Pipeline failed. Check the stage logs." }
  }
}
'@ | Set-Content Jenkinsfile
