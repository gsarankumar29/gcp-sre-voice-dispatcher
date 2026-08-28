from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GCP SRE Voice Dispatcher"
    environment: str = "development"
    log_level: str = "INFO"

    internal_secret_token: str = "development-secret"

    vapi_api_key: str = ""
    vapi_phone_number_id: str = ""
    vapi_assistant_id: str = ""

    engineer_phone_number: str = ""

    dispatch_mode: str = "simulation"

    gcp_project_id: str = ""
    gcp_region: str = "asia-south1"

    allowed_cloud_run_jobs: str = ""
    allowed_cloud_run_services: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def allowed_jobs(self) -> set[str]:
        return {
            job.strip()
            for job in self.allowed_cloud_run_jobs.split(",")
            if job.strip()
        }

    @property
    def allowed_cloud_run_jobs_list(self) -> set[str]:
        return {
            job.strip()
            for job in self.allowed_cloud_run_jobs.split(",")
            if job.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()