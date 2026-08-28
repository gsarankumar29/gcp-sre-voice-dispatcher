from pydantic import BaseModel, Field


class GCPAlertPayload(BaseModel):
    incident_id: str = Field(
        ...,
        min_length=1,
        description="Unique incident identifier"
    )

    job_name: str = Field(
        ...,
        min_length=1,
        description="Affected Cloud Run resource"
    )

    error_message: str = Field(
        ...,
        min_length=1,
        description="Error details"
    )

    severity: str = Field(
        default="CRITICAL"
    )

    resource_type: str = Field(
        default="cloud_run_job"
    )