# Python Cryptographic Authority Infrastructure

The [PyCA](https://github.com/pyca) operates a significant amount of
infrastructure in the form of continuous integration. This repository holds the
configuration for setting up our [Jenkins server](https://ci.cryptography.io), 
as well as the various docker containers we use in testing.

## Ansible

To run the ansible playbook you'll need your SSH public key in the server's
`authorized_keys` and then you can run `./deploy`.

Ansible is responsible for making sure Docker is running on the host,
installing SystemD service files for Caddy and Jenkins, pulling the Caddy and
Jenkins docker images, and making sure they're running.

## Docker Containers

Docker containers are built on merge by Jenkins and then uploaded to [Docker
Hub](https://hub.docker.com/u/pyca/). Each repository on Docker Hub corresponds
to a directory in `runners`.

## Jenkins

An outline of how to set up our jenkins:

* Provision a new server
* Repoint the DNS so that when caddy comes up it can obtain a certificate
* Run the ansible deployment script
* Follow the instructions for adding credentials in `CREDENTIALS.md`
* Set up the plugins (TODO: provision these automatically). A non-exhaustive list:
  * AnsiColor
  * Blue Ocean
  * GitHub Authentication Plugin
  * Pipeline
  * Pipeline Utility Steps
  * Simple Theme Plugin
  * SSH Slaves Plugin
  * Timestamper
* Set up GitHub authentication plugin
  * Under configure global security you'll need to set up the client ID and client secret.
  * Set admin usernames (these are GitHub user names)
* Set up simple theme plugin
  * Under Configure System set the URL of theme CSS to https://cdn.rawgit.com/afonsof/jenkins-material-theme/gh-pages/dist/material-teal.css
* Add non-docker-based nodes (e.g. macOS, FreeBSD, Windows)
  * TODO: more extensive documentation if it's not possible to automate this
* Add docker hub credentials
  * Go to jenkins global credentials and click add credentials
    * Choose username with password
    * Scope set to global
    * id should be `dockerhub-credentials`
    * username and password should be the cryptohubbot user
* Create the primary organization job (New Item -> GitHub Organization)
  * In configuration, under Projects -> GitHub Organization click Advanced.
    * Change include branches from `*` to `master`
    * Check build origin branches
    * Uncheck build origin branches also filed as PRs.
