# GCP SRE Voice Dispatcher

An AI-powered incident dispatcher that receives Google Cloud alerts through Pub/Sub and triggers an automated voice escalation workflow.

The project is designed as an SRE incident automation system for Cloud Run services and jobs.

## Architecture

```text
Cloud Run Job / Service Failure
              │
              ▼
        Google Cloud Alert
              │
              ▼
         Pub/Sub Topic
              │
              ▼
      Pub/Sub Push Subscription
              │
              ▼
        Cloud Run Service
              │
              ▼
     GCP SRE Voice Dispatcher
              │
              ├── Simulation Mode
              │
              └── Vapi Voice Call
                      │
                      ▼
                 SRE Engineer
Features
Receives incident alerts through Google Cloud Pub/Sub
Supports Cloud Run services and jobs
Filters incidents based on severity
Supports CRITICAL, ERROR, and P0 alerts
Decodes Pub/Sub push messages
Triggers outbound voice calls using Vapi
Includes simulation mode for testing
Provides Vapi tool endpoints for incident actions
Supports Cloud Run deployment
Secures Pub/Sub → Cloud Run communication using OIDC
Project Structure
gcp-sre-voice-dispatcher/
│
├── app/
│   ├── api/
│   │   └── vapi_tools.py
│   │
│   ├── models/
│   │   └── alerts.py
│   │
│   ├── security/
│   │   └── auth.py
│   │
│   ├── services/
│   │   └── vapi_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
Prerequisites

Install the following:

Python 3.11+
Google Cloud SDK
Docker
A Google Cloud project
Cloud Run enabled
Pub/Sub enabled

For real voice calls:

Vapi account
Vapi Assistant
Vapi phone number
Local Setup
1. Clone the repository
git clone <YOUR_REPOSITORY_URL>
cd gcp-sre-voice-dispatcher
2. Create a virtual environment
python3 -m venv venv

Activate it:

macOS/Linux
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file.

VAPI_API_KEY=your_vapi_api_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id

ENGINEER_PHONE_NUMBER=+1234567890

INTERNAL_SECRET_TOKEN=your_secret_token

DISPATCH_MODE=simulation
Dispatch Modes
Simulation Mode
DISPATCH_MODE=simulation

No real phone call is made.

The application logs the simulated voice dispatch.

Example:

SIMULATED VOICE DISPATCH

This mode is recommended for development and testing.

Production Mode
DISPATCH_MODE=production

The application sends an outbound call request to Vapi.

Run Locally

Start the FastAPI application:

uvicorn app.main:app --reload

The application will run at:

http://127.0.0.1:8000

Test the health endpoint:

curl http://127.0.0.1:8000/health

Expected response:

{
  "status": "healthy"
}
Test an Alert Locally

Send a simulated critical incident:

curl -X POST http://127.0.0.1:8000/webhook/gcp-alert \
-H "Content-Type: application/json" \
-H "X-Internal-Token: your_secret_token" \
-d '{
  "incident_id": "simulation-test-001",
  "job_name": "sre-test-job",
  "error_message": "Testing simulated voice dispatch",
  "severity": "CRITICAL",
  "resource_type": "cloud_run_job"
}'

Expected response:

{
  "status": "call_initiated",
  "incident_id": "simulation-test-001",
  "resource": "sre-test-job"
}

When using simulation mode, no real phone call is placed.

Pub/Sub Message Format

The Pub/Sub message contains incident information.

Example:

{
  "incident_id": "cloud-run-pubsub-001",
  "job_name": "sre-test-job",
  "error_message": "Cloud Run Job failed",
  "severity": "CRITICAL"
}

The Pub/Sub push message is automatically Base64 encoded by Google Cloud Pub/Sub.

The application decodes the message and processes the alert.

Google Cloud Setup

Set your project ID:

gcloud config set project YOUR_PROJECT_ID

Enable required APIs:

gcloud services enable \
run.googleapis.com \
pubsub.googleapis.com \
cloudbuild.googleapis.com
Create Pub/Sub Topic
gcloud pubsub topics create gcp-sre-alerts
Deploy to Cloud Run

Deploy the application:

gcloud run deploy gcp-sre-voice-dispatcher \
  --source . \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --allow-unauthenticated

After deployment, retrieve the service URL:

gcloud run services describe gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --format="value(status.url)"
Configure Environment Variables

For simulation mode:

gcloud run services update gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --update-env-vars "DISPATCH_MODE=simulation"

For production, configure the required Vapi environment variables.

Example:

gcloud run services update gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --update-env-vars "DISPATCH_MODE=production"
Create Service Account for Pub/Sub

Create a dedicated service account:

gcloud iam service-accounts create pubsub-push-dispatcher \
  --display-name="Pub/Sub Push Dispatcher" \
  --project YOUR_PROJECT_ID

The service account email will be:

pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com
Grant Cloud Run Invoker Permission

Allow the Pub/Sub service account to invoke the Cloud Run service:

gcloud run services add-iam-policy-binding \
gcp-sre-voice-dispatcher \
--region asia-south1 \
--project YOUR_PROJECT_ID \
--member="serviceAccount:pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/run.invoker"
Configure Pub/Sub OIDC Authentication

Grant the Pub/Sub service agent permission to generate tokens:

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
--member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
--role="roles/iam.serviceAccountTokenCreator"

Replace:

PROJECT_NUMBER

with your Google Cloud project number.

Create Pub/Sub Push Subscription

Create the push subscription:

gcloud pubsub subscriptions create gcp-sre-alerts-push \
  --topic=gcp-sre-alerts \
  --push-endpoint="YOUR_CLOUD_RUN_URL/webhook/pubsub-alert" \
  --push-auth-service-account="pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --project=YOUR_PROJECT_ID

Example:

https://your-cloud-run-service.run.app/webhook/pubsub-alert
Test the Complete Pipeline

Publish a test incident:

gcloud pubsub topics publish gcp-sre-alerts \
  --message='{
    "incident_id":"simulation-test-001",
    "job_name":"sre-test-job",
    "error_message":"Testing complete incident pipeline",
    "severity":"CRITICAL"
  }' \
  --project YOUR_PROJECT_ID

The flow will be:

Pub/Sub
   ↓
Push Subscription
   ↓
Cloud Run
   ↓
FastAPI
   ↓
Incident Processing
   ↓
Voice Dispatcher
View Cloud Run Logs
gcloud run services logs read gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --limit 50

In simulation mode, successful processing looks similar to:

Pub/Sub alert received
Alert received
SIMULATED VOICE DISPATCH
Vapi call initiated
POST 200
Vapi Tool Endpoints

The application provides endpoints that can be used by a Vapi assistant during an incident call.

Example endpoint:

POST /webhook/vapi-tools

Supported actions can include:

Acknowledge incident
Retry Cloud Run Job
Trigger incident actions

Example request:

{
  "message": {
    "type": "tool-calls",
    "toolCallList": [
      {
        "id": "cloud-run-test-001",
        "name": "acknowledge_incident",
        "arguments": {
          "incidentId": "production-test-001"
        }
      }
    ]
  }
}
Severity Filtering

Only high-priority incidents trigger escalation.

Supported severities:

CRITICAL
ERROR
P0

Other severity levels are ignored.

Example:

{
  "status": "ignored",
  "reason": "Severity does not require escalation"
}
Testing Modes
Simulation Mode

Recommended for:

Local development
CI/CD testing
Cloud Run pipeline testing
Pub/Sub integration testing
DISPATCH_MODE=simulation

No external phone call is made.

Production Mode

Recommended for real incident escalation.

DISPATCH_MODE=production

A valid Vapi configuration and supported phone number are required.

Current Architecture Status

The following pipeline has been successfully tested:

Pub/Sub Topic
      ↓
Pub/Sub Push Subscription
      ↓
OIDC Authentication
      ↓
Cloud Run
      ↓
FastAPI Webhook
      ↓
Alert Processing
      ↓
Severity Filtering
      ↓
Simulation Voice Dispatch

The complete pipeline successfully returns:

HTTP 200 OK
Future Improvements
Cloud Monitoring alert integration
Automatic incident creation
Retry policies for failed voice dispatches
Dead-letter Pub/Sub queues
Incident database storage
Multiple SRE escalation contacts
Escalation policies
SMS and Slack notifications
Real Vapi production calling
Terraform infrastructure deployment
CI/CD with GitHub Actions
Tech Stack
Python
FastAPI
Google Cloud Run
Google Cloud Pub/Sub
Google Cloud IAM
Vapi
Docker
HTTPX
Author

Saran Kumar

Built as an SRE automation and AI-powered incident response project.


## My recommendation

This README is a good balance for GitHub. It is detailed enough to show:

- your architecture
- Cloud Run knowledge
- Pub/Sub knowledge
- IAM/OIDC authentication
- FastAPI development
- real deployment process
- testing workflow

For a portfolio project, this is much better than an extremely short README because recruiters can actually understand **what you built and how much infrastructure you configured**.
