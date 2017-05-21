if (env.BRANCH_NAME == "master") {
    properties([pipelineTriggers([cron('H/5 * * * *')])])
}

def builders = [:]

def parseConfig(data) {
    // readJSON returns a non-serializable object, which we need to
    // iterate over and store into a new list because pipelines require
    // serializable data.
    configs = []
    for (el in data) {
        configs << el
    }
    return configs
}

stage("Build Configs") {
    node {
        checkout scm
        configs = parseConfig(readJSON(file: 'config.json'))
        for (config in configs) {
            def name = config["tag"]
            def path = config["path"]
            def build_args = ""
            for (build_arg in config["build_args"]) {
                build_args += "--build-arg $build_arg "
            }
            // In jenkinsfiles PRs are named with BRANCH_NAME of "PR-<number>"
            // so only the origin master branch can satisfy this conditional
            def tag = ""
            if (env.BRANCH_NAME == 'master') {
                tag = "-t $name"
            }
            builders[name] = {
                node("docker") {
                        stage("Checkout") {
                            checkout scm
                        }
                        stage("Build") {
                            ansiColor('xterm') {
                                sh "docker build --pull $tag $path $build_args"
                            }
                        }
                        stage("Publish") {
                            // Only publish if this is a merge to master
                            if (env.BRANCH_NAME == 'master') {
                                docker.withRegistry('', 'dockerhub-credentials') {
                                    image = docker.image(name)
                                    image.push()
                                }
                            }
                        }
                }
            }
        }
    }
}

parallel builders

stage("Prune") {
    node("docker") {
        sh "docker image prune -f"
    }
}
