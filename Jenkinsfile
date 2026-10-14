pipeline {
    agent any
    parameters {
        booleanParam(name: 'DEPLOY', defaultValue: true, description: 'Deploy sau khi test và Quality Gate đạt')
    }
    triggers { pollSCM('H/2 * * * *') }
    options {
        skipDefaultCheckout(true)
        skipStagesAfterUnstable()
        disableConcurrentBuilds()
        timeout(time: 25, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
    }
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
        SONAR_PROJECT_KEY = 'my-python-app'
        COMPOSE_PROJECT_NAME = 'my-python-app'
        APP_IMAGE = 'my-python-app'
        APP_PORT = '8000'
        SMOKE_HOST = 'host.docker.internal'
    }
    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
                    env.APP_VERSION = "${env.GIT_COMMIT_SHORT}-${env.BUILD_NUMBER}"
                    env.TEST_IMAGE = "my-python-app-tests:${env.APP_VERSION}"
                }
            }
        }
        stage('Compile') {
            steps {
                sh 'docker build --pull --target test -t "$TEST_IMAGE" .'
            }
        }
        stage('Unit Test') {
            steps {
                sh '''
                    container=$(docker create "$TEST_IMAGE")
                    trap 'docker rm -f "$container" >/dev/null 2>&1 || true' EXIT
                    docker start "$container" >/dev/null
                    docker logs -f "$container"
                    status=$(docker wait "$container")
                    mkdir -p reports dist
                    docker cp "$container:/app/reports/." reports/
                    if [ "$status" -eq 0 ]; then
                        docker cp "$container:/app/dist/." dist/
                    fi
                    exit "$status"
                '''
                sh 'test -s reports/coverage.xml'
            }
            post {
                always {
                    junit testResults: 'reports/junit.xml'
                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/*.xml'
                }
            }
        }
        stage('Package') {
            steps {
                archiveArtifacts artifacts: 'dist/*.whl,dist/*.tar.gz', fingerprint: true
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '"$SCANNER_HOME/bin/sonar-scanner" -Dsonar.projectKey="$SONAR_PROJECT_KEY" -Dsonar.projectVersion="$APP_VERSION"'
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        def gate = waitForQualityGate abortPipeline: true
                        if (gate.status != 'OK') { error "Quality Gate failed: ${gate.status}" }
                    }
                }
            }
        }
        stage('Build image') {
            when { expression { params.DEPLOY } }
            steps {
                withCredentials([string(credentialsId: 'my-python-app-secret-key', variable: 'APP_SECRET_KEY')]) {
                    sh 'docker compose build web'
                }
            }
        }
        stage('Deploy') {
            when { expression { params.DEPLOY } }
            steps {
                withCredentials([string(credentialsId: 'my-python-app-secret-key', variable: 'APP_SECRET_KEY')]) {
                    sh 'docker compose up -d --no-build --pull never --wait --wait-timeout 120 web'
                }
            }
        }
        stage('Smoke test') {
            when { expression { params.DEPLOY } }
            steps {
                withCredentials([string(credentialsId: 'my-python-app-secret-key', variable: 'APP_SECRET_KEY')]) {
                sh '''
                    code=$(curl --connect-timeout 3 --max-time 10 -s -o /dev/null -w '%{http_code}' "http://$SMOKE_HOST:$APP_PORT/health")
                    test "$code" = 200
                    container=$(docker compose ps --quiet web)
                    docker exec "$container" python -c 'import json, http.cookiejar, urllib.request; opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())); token=json.load(opener.open("http://localhost:8080/api/csrf", timeout=5))["csrf_token"]; request=urllib.request.Request("http://localhost:8080/api/calculate", data=json.dumps({"operation":"add","a":2,"b":3}).encode(), headers={"Content-Type":"application/json","X-CSRFToken":token}); response=opener.open(request, timeout=5); assert json.load(response)["result"] == 5'
                    docker compose ps
                '''
                }
            }
        }
    }
    post {
        success { echo "CI/CD thành công: ${env.APP_VERSION}" }
        unsuccessful { echo 'Pipeline không đạt. Xem stage bị lỗi; các bước triển khai phía sau bị bỏ qua.' }
    }
}
