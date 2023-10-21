# Synthboi

This is a simple Flask server that helps manage various tasks

## Public Registry
Images are published on our ECR 
https://gallery.ecr.aws/cyberfurz/mastodon-power-toys

## Environment Variables

| Environment Variable  | Default                              | Description                                         |
|-----------------------|--------------------------------------|-----------------------------------------------------|
| MASTODON_API_URL      | https://mastodon.social              | Mastodon Server                                     |
| MASTODON_ACCESS_TOKEN |                                      | Mastodon Access Token with Admin:Read               |
| API_KEY               | 0178b552-0503-450b-b9b0-6fdc8680a258 | This is the Authorization header for secured routes |
| PORT                  | 5000                                 | Port for server to run on                           |
| SYNAPSE_SERVER_URL    | https://matrix.org                   | Replace with your homeserver url                    |
| LOGIN_ACESS_TOKEN     | syt_XXXXXXXXXXXXXXXXXXX              | Replace with a syanpse admin access token           |
