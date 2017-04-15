FROM jenkinsci/jenkins:lts

USER root
RUN apt-get -qq update
RUN apt-get -qq -y install curl

RUN curl -sSL https://get.docker.com/ | sh

RUN usermod -a -G staff,docker jenkins

USER jenkins
