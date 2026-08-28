import base64
import json
import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import ValidationError

from app.api.vapi_tools import router as vapi_tools_router
from app.models.alerts import GCPAlertPayload
from app.security.auth import verify_internal_token
from app.services.vapi_service import VapiService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="GCP SRE Voice Dispatcher",
    description=(
        "AI-powered incident dispatcher for "
        "Cloud Run Services and Jobs"
    ),
    version="1.0.0",
)

app.include_router(vapi_tools_router)

vapi_service = VapiService()


ALLOWED_SEVERITIES = {
    "CRITICAL",
    "ERROR",
    "P0",
}


@app.get("/")
async def root():
    return {
        "message": "GCP SRE Voice Dispatcher is running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


async def process_alert(
    payload: GCPAlertPayload,
):
    """
    Shared alert processing logic.

    Used by:
    - Direct GCP alert webhook
    - Pub/Sub alert webhook
    """

    severity = payload.severity.upper()

    logger.info(
        "Alert received | incident_id=%s | "
        "severity=%s | resource=%s",
        payload.incident_id,
        severity,
        payload.job_name,
    )

    # Severity guardrail
    if severity not in ALLOWED_SEVERITIES:

        logger.info(
            "Alert ignored | incident_id=%s | "
            "reason=severity_filter",
            payload.incident_id,
        )

        return {
            "status": "ignored",
            "incident_id": payload.incident_id,
            "reason": (
                f"Severity '{severity}' "
                "does not require escalation"
            ),
        }

    try:

        call_response = (
            await vapi_service.create_outbound_call(
                incident_id=payload.incident_id,
                resource_name=payload.job_name,
                error_message=payload.error_message,
            )
        )

        logger.info(
            "Vapi call initiated | incident_id=%s",
            payload.incident_id,
        )

        return {
            "status": "call_initiated",
            "incident_id": payload.incident_id,
            "resource": payload.job_name,
            "vapi_call": call_response,
        }

    except Exception:

        logger.exception(
            "Failed to initiate Vapi call | "
            "incident_id=%s",
            payload.incident_id,
        )

        raise HTTPException(
            status_code=502,
            detail="Failed to initiate outbound call",
        )


@app.post("/webhook/gcp-alert")
async def receive_gcp_alert(
    payload: GCPAlertPayload,
    _: None = Depends(verify_internal_token),
):

    return await process_alert(payload)


@app.post("/webhook/pubsub-alert")
async def receive_pubsub_alert(
    request: Request,
):

    try:

        body = await request.json()

        message = body.get("message")

        if not message:
            raise HTTPException(
                status_code=400,
                detail="Invalid Pub/Sub message",
            )

        encoded_data = message.get("data")

        if not encoded_data:
            raise HTTPException(
                status_code=400,
                detail="Pub/Sub message data is missing",
            )

        decoded_bytes = base64.b64decode(
            encoded_data
        )

        decoded_data = decoded_bytes.decode(
            "utf-8"
        )

        alert_data = json.loads(
            decoded_data
        )

        payload = GCPAlertPayload(
            **alert_data
        )

        logger.info(
            "Pub/Sub alert received | "
            "message_id=%s | incident_id=%s",
            message.get("messageId"),
            payload.incident_id,
        )

        return await process_alert(payload)

    except HTTPException:
        raise

    except (
        ValueError,
        ValidationError,
        json.JSONDecodeError,
    ) as error:

        logger.exception(
            "Invalid Pub/Sub alert payload"
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Pub/Sub alert payload"
            ),
        ) from error

    except Exception:

        logger.exception(
            "Failed to process Pub/Sub alert"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process Pub/Sub alert",
        )