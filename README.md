# Fly Audio Transcoder

This repo contains a basic implementation of an API that transcodes audio from WAV format to MP3 format. This implementation lets you spin up a Fly Machine on demand to handle a specific transcoding job. To do this, the API calls Fly's Machines API directly, which means it doesn't require flyctl (the Fly command line tool) for managing and scaling infrastructure. The purpose of this implementation is to showcase the capabilities and flexibility of the Machines API.

## Overview

The repo is split into subdirectories:

1. `/fly-audio-transcoder-api` contains the API code.
2. `/fly-audio-transcoder-worker` contains the worker code.

The API and Worker projects both contain a `fly.toml` and `Dockerfile` file for easy deployment to Fly.io.

Technically speaking, the API project is a FastAPI app that creates and manages jobs with MongoDB as a database, interfaces with Cloudflare R2 for generating presigned download and upload URLs, and orchestrates Fly Machines with the `fly-python-sdk` package (which by the way is not stable yet, so don't use it in production). The Worker project is a simple Bash script that makes various calls to `curl`, `jq`, and `ffmpeg` to transcode the file.

## How to Deploy

To deploy this implementation, you'll need to create two Fly apps.

### Build the Worker App

To build (not deploy!) the Worker app, follow these steps:

1. `cd` into the `fly-audio-transcoder-worker` directory, and run `fly apps create`.
2. Run `fly deploy --build-only --push` to build the image and push it to the registry. Make note of the image reference (looks something like like `registry.fly.io/<WORKER_APP_NAME>:deployment..."`).

### Deploy the API App

To deploy the API app, follow these steps:

1. `cd` into the `fly-audio-transcoder-api` directory, and run `fly launch`. Don't deploy yet.
2. Create a Flycast (private IPV6) address for the API app with `fly ips allocate-v6 --private`.
3. Set required secrets for the API app (listed below) with `fly secrets set AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... etc...`.
4. Deploy the API with `fly deploy --vm-size shared-cpu-2x --vm-memory 1024`.

#### Required API App Secrets

|ENVIRONMENT VARIABLE | DESCRIPTION                                                                                                                  |
|---------------------|------------------------------------------------------------------------------------------------------------------------------|
|AWS_ACCESS_KEY_ID    |Access Key ID for interfacing with S3 or an S3-compatible alternative.                                                        |
|AWS_SECRET_ACCESS_KEY|Secret Access Key for interfacing with S3 or an S3-compatible alternative.                                                    |
|S3_ENDPOINT_URL      |Endpoint URL for S3 or an S3-compatible alternative                                                                           |
|DB_URL               |A MongoDB connection string.                                                                                                  |
|FLY_API_TOKEN        |API token (personal access token or [deploy token](https://fly.io/docs/reference/deploy-tokens/)) for managing the Worker app.|
|FLY_ORG_SLUG         |The slug of the Org where API and Worker apps are located.                                                                    |
|FLY_WORKER_APP_NAME  |The app name of the Worker app.                                                                                               |
|FLY_WORKER_IMAGE     |The image reference for the Worker app's image (generated in Step 2 of the "Build the Worker section above).                  |