# Cloud Run Deployment

This repository builds and deploys only the survey follow-up API. The `infra/followup/cloudbuild.yaml` file handles the entire pipeline (build, push, deploy) against the root `Dockerfile`.

## Usage

1. **Create a Cloud Build trigger** that points at this repo and uses `infra/followup/cloudbuild.yaml` as the build configuration.
2. **Optional filters**: include `followup/**`, `shared/**`, `Dockerfile`, `pyproject.toml`, `poetry.lock`, and `infra/followup/**` to ensure only relevant changes trigger redeploys.
3. **Customize substitutions** per environment (service name, region, image registry) either in the trigger UI or by editing the `_SERVICE`, `_REGION`, and `_IMAGE` values inside `infra/followup/cloudbuild.yaml`.

For additional agents, create separate repositories (or copy this structure) so each service keeps an independent Dockerfile and deployment pipeline.
