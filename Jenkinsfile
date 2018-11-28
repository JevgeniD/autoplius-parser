timestamps {
    try {
        stage('Git checkout') {
            gitCheckout()
        }

        stage('Install dependencies') {
            sh "python3 -m pip install -r reqs.txt"
        }

        stage('Run parser') {
            sh "python3 parser.py"
        }
    } catch (error) {
        currentBuild.result = 'FAILED'
        throw (error)
    }
}

def gitCheckout() {
    git branch: 'master', changelog: false, credentialsId: 'd894b982-3d7e-4932-bcb9-4acf949052f3', url: 'git@github.com:JevgeniD/autoplius-parser.git'
}