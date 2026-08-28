import json
import logging

from fastapi import APIRouter, Request

from app.services.cloud_run_service import (
    GCPCloudRunService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/webhook",
    tags=["Vapi Tools"],
)


gcp_service = GCPCloudRunService()


@router.post("/vapi-tools")
async def handle_vapi_tools(
    request: Request,
):

    payload = await request.json()

    message = payload.get(
        "message",
        {}
    )

    message_type = message.get(
        "type"
    )

    # Ignore non-tool events.
    if message_type != "tool-calls":
        return {
            "results": []
        }

    tool_calls = message.get(
        "toolCallList",
        []
    )

    results = []

    for tool_call in tool_calls:

        tool_call_id = tool_call.get("id")

        tool_name = tool_call.get("name")

        # Vapi payload versions can represent
        # arguments differently.
        arguments = (
            tool_call.get("arguments")
            or tool_call.get("parameters")
            or {}
        )

        logger.info(
            "Vapi tool called | tool=%s",
            tool_name,
        )

        try:

            if tool_name == "retry_gcp_job":

                job_name = arguments.get(
                    "jobName"
                )

                if not job_name:
                    raise ValueError(
                        "jobName is required"
                    )

                result = (
                    await gcp_service.retry_job(
                        job_name
                    )
                )

                result_message = (
                    f"Cloud Run Job '{job_name}' "
                    "has been triggered successfully."
                )

                logger.info(
                    "Job retry successful | "
                    "job=%s",
                    job_name,
                )

            elif (
                tool_name
                == "acknowledge_incident"
            ):

                incident_id = arguments.get(
                    "incidentId"
                )

                if not incident_id:
                    raise ValueError(
                        "incidentId is required"
                    )

                # Temporary implementation.
                # We will replace this with persistent
                # incident storage later.
                result = {
                    "status": "acknowledged",
                    "incident_id": incident_id,
                }

                result_message = (
                    f"Incident '{incident_id}' "
                    "has been acknowledged."
                )

                logger.info(
                    "Incident acknowledged | "
                    "incident=%s",
                    incident_id,
                )

            else:

                raise ValueError(
                    f"Unsupported tool: {tool_name}"
                )

        except Exception as exc:

            logger.exception(
                "Vapi tool execution failed | "
                "tool=%s",
                tool_name,
            )

            result_message = (
                f"Tool execution failed: {str(exc)}"
            )

        results.append(
            {
                "toolCallId": tool_call_id,
                "result": result_message,
            }
        )

    return {
        "results": results
    }