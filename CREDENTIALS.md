The PyCA infrastructure requires a variety of credentials to function.

## Hubot

The pyca/hubot container runs as a docker service in a docker swarm. It requires the following environment variables:

### `HUBOT_GITHUB_TOKEN`

Used to make requests to the GitHub API with reasonable rate limits.

Creation/Rotation:

* Using the cryptojenkins GitHub user
  * Delete the existing `hubot` personal access token under Settings:Personal Access Tokens (if rotating)
  * Generate a new token with all scopes unchecked and name it hubot.
  * Write the resulting token (a hexadecimal string) to a file.
* `docker secret rm HUBOT_GITHUB_TOKEN` (if rotating)
* `docker secret create HUBOT_GITHUB_TOKEN /file/containing/token`
