pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Compile') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            python -m compileall src/myapp
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                            python -m compileall src\\myapp
                        '''
                    }
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            export PYTHONPATH=src
                            pytest tests/ --junitxml=result.xml
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            set PYTHONPATH=src
                            pytest tests/ --junitxml=result.xml
                        '''
                    }
                }
            }
            post {
                always {
                    junit 'result.xml'
                }
            }
        }

        stage('Package') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            python setup.py sdist bdist_wheel
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            python setup.py sdist bdist_wheel
                        '''
                    }
                }
                archiveArtifacts artifacts: 'dist/*.whl, dist/*.tar.gz', fingerprint: true
            }
        }
    }
}
