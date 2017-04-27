FROM node:7.9-slim

RUN apt-get -qq update
RUN apt-get -qq -y upgrade
RUN apt-get install -qq -y runit

ENV HUBOT_IRC_SERVER irc.freenode.net
ENV HUBOT_IRC_ROOMS #cryptography-dev
ENV HUBOT_IRC_NICK PyCA_Hubot
ENV HUBOT_GITHUB_REPO pyca/cryptography
ENV HUBOT_GITHUB_ISSUE_LINK_IGNORE_USERS github|hubot|cryptojenkins

RUN groupadd -g 501 hubot
RUN useradd -m -u 501 -g 501 hubot

RUN mkdir -p /home/hubot/.config/configstore
RUN mkdir /home/hubot/bot
RUN chown -R hubot:hubot /home/hubot

USER hubot
WORKDIR /home/hubot/bot

COPY data/package.json /home/hubot/bot/
COPY data/scripts/ /home/hubot/bot/scripts
COPY data/bin/ /home/hubot/bot/bin

RUN npm install

# Requires a docker secret HUBOT_GITHUB_TOKEN
CMD ["chpst", "-e", "/run/secrets/", "bin/hubot", "-a", "irc"]
