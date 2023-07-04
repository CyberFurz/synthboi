# Mastodon Power Toys

This is a simple Flask server that helps you do some tasks for your Mastodon server

## Public Registry
Images are published on our ECR 
https://gallery.ecr.aws/c9a1z9d7/mastodon-power-toys

## Environment Variables

| Environment Variable  | Default                              | Description                                         |
|-----------------------|--------------------------------------|-----------------------------------------------------|
| MASTODON_API_URL      | https://mastodon.social              | Mastodon Server                                     |
| MASTODON_ACCESS_TOKEN |                                      | Mastodon Access Token with Admin:Read               |
| API_KEY               | 0178b552-0503-450b-b9b0-6fdc8680a258 | This is the Authorization header for secured routes |
| PORT                  | 5000                                 | Port for server to run on                           |