import asyncio
import logging

from google.api_core.client_options import ClientOptions
from google.cloud import run_v2

from app.config import settings


logger = logging.getLogger(__name__)


class GCPCloudRunService:

    def __init__(self):

        api_endpoint = (
            f"{settings.gcp_region}-run.googleapis.com"
        )

        self.client = run_v2.JobsClient(
            client_options=ClientOptions(
                api_endpoint=api_endpoint
            )
        )

    async def retry_job(
        self,
        job_name: str,
    ) -> dict:

        if (
            job_name
            not in settings.allowed_cloud_run_jobs_list
        ):
            raise PermissionError(
                f"Job '{job_name}' is not allowed"
            )

        full_job_name = (
            f"projects/{settings.gcp_project_id}"
            f"/locations/{settings.gcp_region}"
            f"/jobs/{job_name}"
        )

        logger.info(
            "Triggering Cloud Run Job | job=%s",
            full_job_name,
        )

        request = run_v2.RunJobRequest(
            name=full_job_name
        )

        operation = await asyncio.to_thread(
            self.client.run_job,
            request=request,
        )

        logger.info(
            "Cloud Run Job execution started | job=%s",
            job_name,
        )

        return {
            "status": "started",
            "job_name": job_name,
        }