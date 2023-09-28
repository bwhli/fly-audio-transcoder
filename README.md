# Fly Audio Transcoder

This repo contains a basic implementation of an API that transcodes audio from WAV format to MP3 format. This implementation lets you spin up a Fly Machine on demand to handle a specific transcoding job. To do this, the API calls Fly's Machines API directly, which means it doesn't require flyctl (the Fly command line tool) for managing and scaling infrastructure.

But why would anyone want to use Fly without flyctl? While flyctl is indeed awesome, I believe it's best suited for smaller-scale and/or tightly-scoped tasks. By "smaller-scale", I mean dozens or hundreds of Machines. By "tightly-scoped", I mean all the Machines within an app are running the same code without customized per-Machine state and workloads defined at startup time. So, if you have a webapp that you want to deploy around the world, flyctl is the way to go. For a use case like an audio transcoding service, it could make more sense to bypass the abstractions provided by flyctl, and utilize the infrastructure directly – that way you won't have to deal with the side effects introduced by using flyctl as a "translator" between your API and Fly's infrastructure.

This project implements an easy to understand pattern.

1. Schedule jobs with an API.
2. Create job-aware Machines that run jobs and destroy themselves afterward.

IMO, Fly is the best place to implement this kind of pattern for three reasons:

1. Spinning up a Machine is almost instant. Depending on the size of the worker image, you can have something up and running within a few seconds.
2. You only get billed when a Machine is up and running. There's no need to keep a server running 24/7 to listen for tasks.
3. You can bring your entire application stack. Unlike traditional serverless offerings with restrictive runtimes, Fly also uses the Dockerfile standard to seed the filesystem on a real VM (not a container).

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
3. Set required secrets for the API app (shown below) with `fly secrets set AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... etc...`.
4. Deploy the API with `fly deploy --vm-size shared-cpu-2x --vm-memory 1024`.

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

## How it Works

To create a new job, make a POST request to `/jobs/`. The request body is a JSON payload that specifies the target format details.

```
# The 
curl -X POST \
     -H "Content-Type: application/json" \
     --data '{"transcode": {"format": {"extension": "mp3", "bit_depth": 16, "bit_rate": 192, "sample_rate": 44100}}}' \
     "https://<YOUR_API_APP_NAME>.fly.dev/jobs/"
```

The response looks like this:

```
{
    '_id': 'b86e9d25-53cb-4421-a19d-cb65f8e2f574',
    'status': 'created',
    'machine_id': None,
    'source': {
        'download_url': None,
        'upload_url': 'https://<S3_ENDPOINT_URL>/<S3_BUCKET_NAME>/sources/b86e9d25-53cb-4421-a19d-cb65f8e2f574...'
    },
    'transcode': {
        'format': {'extension': 'mp3', 'bit_depth': 16, 'bit_rate': 192, 'sample_rate': 44100},
        'download_url': None,
        'upload_url': None
    }
}
```

Upload a WAV file with the URL stored in `source["upload_url"]`:

```
curl -X PUT \
     -H "Content-Type: audio/wav" \
     -H "Content-Disposition: attachment;filename=<JOB_ID>.wav" \
     --data-binary "@/path/to/test.wav" \
     https://<S3_ENDPOINT_URL>/<S3_BUCKET_NAME>/sources/b86e9d25-53cb-4421-a19d-cb65f8e2f574...
```

Start the job with a POST request to `/jobs/<JOB_ID>/status/started/`:

```
curl -X POST "<API_URL>/jobs/<JOB_ID>/status/started/"
```

This endpoint creates a Fly Machine like so:

```
# Set the API URL and Job ID in the Machine's environment (only applies for this specific Machine).
machine_env = {
    "API_URL": f"http://{FLY_APP_NAME}.flycast",
    "JOB_ID": f"{job.id}",
}

# Create Fly Machine config to pass to FlyMachine object.
machine_config = FlyMachineConfig(
    env=machine_env,
    image=FLY_WORKER_IMAGE,
    size="performance-2x",
    auto_destroy=True,
    restart=FlyMachineConfigRestart(policy="no"),
)

# Fetch the Worker app.
worker_app = Fly(FLY_API_TOKEN).Org(FLY_ORG_SLUG).App(FLY_WORKER_APP_NAME)

# Create the Machine in the Worker app.
machine = await worker_app.create_machine(
    FlyMachine(name=str(job.id), config=machine_config),
)
```

At this point, the Machine will start up within a few seconds, complete the task, upload the transcoded MP3 file to S3, and all the `/jobs/<JOB_ID>/status/completed/` to generate a presigned download URL for the transcoded file. Since the Machine was configured with `auto_destroy=True`, it'll automatically destroy itself after completing its assigned job.

## What's Next?

Nothing!

The purpose of this project was to demonstrate how to use Fly's Machines API to run compute workloads on demand.