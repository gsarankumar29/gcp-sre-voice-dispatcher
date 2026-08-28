import logging
import httpx

from app.config import settings


logger = logging.getLogger(__name__)


class VapiService:

    BASE_URL = "https://api.vapi.ai"

    async def create_outbound_call(
        self,
        incident_id: str,
        resource_name: str,
        error_message: str,
    ) -> dict:

        # --------------------------------
        # SIMULATION MODE
        # --------------------------------

        if settings.dispatch_mode.lower() == "simulation":

            logger.info(
                "SIMULATED VOICE DISPATCH | "
                "incident_id=%s | resource=%s | error=%s",
                incident_id,
                resource_name,
                error_message,
            )

            return {
                "status": "simulated_call_initiated",
                "incident_id": incident_id,
                "resource": resource_name,
                "message": (
                    "Voice dispatch simulated successfully"
                ),
            }

        # --------------------------------
        # REAL VAPI MODE
        # --------------------------------

        payload = {
            "assistantId": settings.vapi_assistant_id,
            "phoneNumberId": settings.vapi_phone_number_id,
            "customer": {
                "number": settings.engineer_phone_number,
            },
            "assistantOverrides": {
                "variableValues": {
                    "jobName": resource_name,
                    "errorDetails": error_message[:400],
                    "incidentId": incident_id,
                }
            },
        }

        headers = {
            "Authorization": f"Bearer {settings.vapi_api_key}",
            "Content-Type": "application/json",
        }

        logger.info(
            "Sending Vapi call request | "
            "assistant_id_configured=%s | "
            "phone_number_id_configured=%s | "
            "engineer_number_configured=%s",
            bool(settings.vapi_assistant_id),
            bool(settings.vapi_phone_number_id),
            bool(settings.engineer_phone_number),
        )

        timeout = httpx.Timeout(20.0)

        async with httpx.AsyncClient(
            timeout=timeout,
        ) as client:

            response = await client.post(
                f"{self.BASE_URL}/call",
                json=payload,
                headers=headers,
            )

            if response.is_error:

                logger.error(
                    "VAPI RESPONSE | status=%s | body=%s",
                    response.status_code,
                    response.text,
                )

            response.raise_for_status()

            return response.json()