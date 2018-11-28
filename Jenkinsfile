timestamps {
    node {
        try {
            stage('Git checkout') {
                gitCheckout()
            }
            
            stage('Install dependencies') {
                sh "python3 -m pip install -r reqs.txt"
            }

            stage('Run parser') {
                runParser = sh script: 'python3 parser.py', returnStdout: true
                expectedMessage = "New items appeared"

                if (runParser.contains(expectedMessage)) {
                    sendEmailNotification()
                    showListOfCars()
                }
            }
        } catch (error) {
            currentBuild.result = 'FAILED'
            throw (error)
        }
    }
}

def gitCheckout() {
    git branch: 'master', changelog: false, credentialsId: 'd894b982-3d7e-4932-bcb9-4acf949052f3', url: 'git@github.com:JevgeniD/autoplius-parser.git'
}

def sendEmailNotification() {
    emailext body: "New cars appeared\n ${currentBuild.currentResult}: Job ${env.JOB_NAME} build: ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}",
    recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
    subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}"
}

def showListOfCars() {
    sh "cat result.csv"
}