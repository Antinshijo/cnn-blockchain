pipeline {
    agent any

    environment {
        EC2_IP = "13.201.161.221"
        PROJECT_PATH = "/home/ubuntu/cnn-blockchain"
    }

    stages {
        stage('Pull Latest Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/Antinshijo/cnn-blockchain.git'
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh """
ssh -o StrictHostKeyChecking=no ubuntu@${EC2_IP} << EOF
cd ${PROJECT_PATH}
git pull origin main
pkill -f "python app.py" || true
source venv/bin/activate
nohup python app.py > output.log 2>&1 &
EOF
"""
                }
            }
        }
    }
}
