pipeline {
    agent any

    environment {
        EC2_IP = "65.1.64.109"   // un EC2 IP
        PROJECT_PATH = "/root/project/cnn-blockchain"
    }

    stages {

        stage('Pull Latest Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Antinshijo/cnn-blockchain.git'
            }
        }

        stage('Deploy to EC2') {
            steps {
                sh """
                ssh -o StrictHostKeyChecking=no root@${EC2_IP} << 'EOF'
                
                cd ${PROJECT_PATH}
                
                git pull origin main
                
                pkill -f python || true
                
                source venv/bin/activate
                
                nohup python app.py > output.log 2>&1 &
                
                EOF
                """
            }
        }
    }
}
