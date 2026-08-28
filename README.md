# 🚨 GCP SRE Voice Dispatcher

An AI-powered SRE incident response system that receives Google Cloud alerts through Pub/Sub and automatically triggers a voice-based escalation workflow.

The project is designed for monitoring and responding to critical failures involving **Google Cloud Run services and jobs**.

Instead of relying only on engineers manually checking dashboards, the system processes critical incidents and initiates an automated escalation workflow.

> ⚠️ The project currently supports a fully tested simulation workflow. Real production voice calling depends on Vapi account configuration, supported phone numbers, and subscription capabilities.

---

# ✨ What Does This Project Do?

The system processes critical infrastructure alerts through the following pipeline:

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
              ▼
      Severity Evaluation
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   Ignored      Critical Alert
                     │
                     ▼
              Voice Dispatch
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
       Simulation Mode    Production Mode
                              │
                              ▼
                          Vapi API
                              │
                              ▼
                       On-Call Engineer

The system is designed to automatically escalate incidents that require immediate attention.

🎯 Why This Project?

Modern SRE teams often use platforms such as:

PagerDuty
Splunk On-Call
Opsgenie

These platforms provide complete incident management and escalation systems.

This project is not intended to replace enterprise incident management platforms.

Instead, it demonstrates how an engineer can build a custom incident automation workflow using:

Google Cloud
Pub/Sub
Cloud Run
FastAPI
AI Voice Agents
Vapi
Function Calling

The project focuses on the integration between cloud infrastructure failures and AI-powered voice interactions.

🚀 Features
Receives incident alerts through Google Cloud Pub/Sub
Supports Cloud Run services and jobs
Filters incidents based on severity
Supports CRITICAL, ERROR, and P0 alerts
Decodes Pub/Sub push messages
Secure Pub/Sub → Cloud Run communication using OIDC
Supports simulation mode for testing
Supports production voice dispatch through Vapi
Provides Vapi tool endpoints
Supports incident acknowledgment
Designed for Cloud Run deployment
Provides detailed application logs
Supports end-to-end Pub/Sub testing
🏗 Architecture
                     GOOGLE CLOUD

        ┌─────────────────────────────┐
        │                             │
        │ Cloud Run Service / Job     │
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
                Monitoring Alert
                       │
                       ▼
                Pub/Sub Topic
                       │
                       ▼
           Pub/Sub Push Subscription
                       │
                 OIDC Authentication
                       │
                       ▼
              Cloud Run Service
                       │
                       ▼
        ┌──────────────────────────────┐
        │                              │
        │  GCP SRE Voice Dispatcher    │
        │                              │
        │        FastAPI API            │
        │                              │
        └──────────────┬───────────────┘
                       │
                       ▼
              Severity Filtering
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
          Low Priority      Critical
            Ignore             │
                               ▼
                       Dispatch Service
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
           Simulation Mode             Production Mode
                                             │
                                             ▼
                                          Vapi API
                                             │
                                             ▼
                                      Voice Call
                                             │
                                             ▼
                                      SRE Engineer
📁 Project Structure
gcp-sre-voice-dispatcher/
│
├── app/
│   │
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
│
├── requirements.txt
│
├── .env.example
│
└── README.md
🛠 Tech Stack
Backend
Python
FastAPI
HTTPX
Google Cloud
Cloud Run
Cloud Pub/Sub
Google Cloud IAM
Cloud Build
AI and Voice
Vapi
AI Voice Assistant
Function Calling
Infrastructure
Docker
Google Cloud SDK
📋 Prerequisites

Install the following:

Python 3.11+
Google Cloud SDK
Docker
Google Cloud Project
Cloud Run API enabled
Pub/Sub API enabled

For production voice calling:

Vapi account
Vapi API key
Vapi Assistant
Vapi phone number
Supported destination phone number
💻 Local Setup
1. Clone the Repository
git clone <YOUR_REPOSITORY_URL>
cd gcp-sre-voice-dispatcher
2. Create a Virtual Environment
python3 -m venv venv

Activate it:

macOS / Linux
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file.

Example:

VAPI_API_KEY=your_vapi_api_key

VAPI_ASSISTANT_ID=your_vapi_assistant_id

VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id

ENGINEER_PHONE_NUMBER=+1234567890

INTERNAL_SECRET_TOKEN=your_secret_token

DISPATCH_MODE=simulation
⚙️ Dispatch Modes

The application supports two modes.

🧪 Simulation Mode
DISPATCH_MODE=simulation

No real phone call is made.

The system simulates the voice dispatch and logs the incident.

Example:

SIMULATED VOICE DISPATCH
incident_id=simulation-test-001
resource=sre-test-job

Recommended for:

Local development
CI/CD testing
Cloud Run testing
Pub/Sub integration testing
Portfolio demonstrations
📞 Production Mode
DISPATCH_MODE=production

The application sends an outbound call request to Vapi.

Example flow:

Critical Alert
      ↓
FastAPI
      ↓
Vapi API
      ↓
Outbound Voice Call
      ↓
Engineer

Production mode requires:

Valid Vapi API key
Valid Vapi Assistant ID
Valid Vapi Phone Number ID
Supported destination phone number
Vapi subscription that supports outbound calling
⚠️ Current Voice Calling Limitation

The Pub/Sub → Cloud Run → FastAPI → Simulation pipeline has been successfully tested.

However, real production voice calls may fail depending on Vapi account limitations.

For example:

Free Vapi numbers do not support international calls.

Therefore, if the destination engineer is located in a country not supported by the configured Vapi phone number, the outbound call will not be completed.

The project includes simulation mode to allow the complete infrastructure pipeline to be tested without requiring real phone calls.

▶️ Run Locally

Start the FastAPI application:

uvicorn app.main:app --reload

The application will run at:

http://127.0.0.1:8000
❤️ Health Check

Test the health endpoint:

curl http://127.0.0.1:8000/health

Expected response:

{
  "status": "healthy"
}
🧪 Test an Alert Locally

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

📩 Pub/Sub Message Format

Example incident message:

{
  "incident_id": "cloud-run-pubsub-001",
  "job_name": "sre-test-job",
  "error_message": "Cloud Run Job failed",
  "severity": "CRITICAL"
}

Google Cloud Pub/Sub automatically sends push messages using Base64 encoding.

The application:

Receives the Pub/Sub push request
Decodes the Base64 message
Parses the incident
Evaluates the severity
Initiates the escalation workflow
☁️ Google Cloud Setup

Set your Google Cloud project:

gcloud config set project YOUR_PROJECT_ID

Enable required APIs:

gcloud services enable \
run.googleapis.com \
pubsub.googleapis.com \
cloudbuild.googleapis.com
📢 Create Pub/Sub Topic

Create the incident topic:

gcloud pubsub topics create gcp-sre-alerts
🚀 Deploy to Cloud Run

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

Example output:

https://your-cloud-run-service.run.app
⚙️ Configure Simulation Mode on Cloud Run

For simulation mode:

gcloud run services update gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --update-env-vars "DISPATCH_MODE=simulation"

Verify:

gcloud run services describe gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID
📞 Configure Production Mode

For production:

gcloud run services update gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --update-env-vars "DISPATCH_MODE=production"

Production mode requires valid Vapi configuration.

🔐 Create Service Account for Pub/Sub

Create a dedicated service account:

gcloud iam service-accounts create pubsub-push-dispatcher \
  --display-name="Pub/Sub Push Dispatcher" \
  --project YOUR_PROJECT_ID

The service account will look similar to:

pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com
🔑 Grant Cloud Run Invoker Permission

Allow the Pub/Sub service account to invoke the Cloud Run service:

gcloud run services add-iam-policy-binding \
gcp-sre-voice-dispatcher \
--region asia-south1 \
--project YOUR_PROJECT_ID \
--member="serviceAccount:pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/run.invoker"
🔒 Configure Pub/Sub OIDC Authentication

Pub/Sub requires permission to generate OIDC tokens.

Grant the Pub/Sub service agent:

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
--member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
--role="roles/iam.serviceAccountTokenCreator"

Replace:

PROJECT_NUMBER

with your Google Cloud project number.

📬 Create Pub/Sub Push Subscription

Create the push subscription:

gcloud pubsub subscriptions create gcp-sre-alerts-push \
  --topic=gcp-sre-alerts \
  --push-endpoint="YOUR_CLOUD_RUN_URL/webhook/pubsub-alert" \
  --push-auth-service-account="pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --project=YOUR_PROJECT_ID

Example:

https://your-cloud-run-service.run.app/webhook/pubsub-alert
🧪 Test the Complete Pipeline

Publish a test incident:

gcloud pubsub topics publish gcp-sre-alerts \
  --message='{
    "incident_id":"simulation-test-001",
    "job_name":"sre-test-job",
    "error_message":"Testing complete incident pipeline",
    "severity":"CRITICAL"
  }' \
  --project YOUR_PROJECT_ID

The complete flow:

Pub/Sub
   ↓
Push Subscription
   ↓
OIDC Authentication
   ↓
Cloud Run
   ↓
FastAPI Webhook
   ↓
Pub/Sub Message Decoding
   ↓
Incident Processing
   ↓
Severity Filtering
   ↓
Voice Dispatcher
📊 View Cloud Run Logs

View recent logs:

gcloud run services logs read gcp-sre-voice-dispatcher \
  --region asia-south1 \
  --project YOUR_PROJECT_ID \
  --limit 50

Successful simulation output looks similar to:

Pub/Sub alert received

Alert received

SIMULATED VOICE DISPATCH

Vapi call initiated

POST 200 OK
🛠 Vapi Tool Endpoints

The application provides endpoints that can be used by the Vapi assistant during an incident call.

Endpoint:

POST /webhook/vapi-tools

The voice assistant can call backend functions during an incident conversation.

Potential actions include:

Acknowledge incident
Retry Cloud Run Job
Check service status
Trigger remediation actions
Example Vapi Tool Request
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

Example response:

{
  "results": [
    {
      "toolCallId": "cloud-run-test-001",
      "result": "Incident 'production-test-001' has been acknowledged."
    }
  ]
}
🚨 Severity Filtering

Only high-priority incidents trigger escalation.

Currently supported severities:

CRITICAL
ERROR
P0

Other severity levels are ignored.

Example response:

{
  "status": "ignored",
  "reason": "Severity does not require escalation"
}
🧪 Testing Modes
Simulation Mode

Recommended for:

Local development
Cloud Run testing
CI/CD testing
Pub/Sub integration testing
Infrastructure demonstrations
DISPATCH_MODE=simulation

The application does not contact external phone numbers.

Production Mode

Recommended for real incident escalation.

DISPATCH_MODE=production

Requirements:

Valid Vapi API key
Valid Assistant ID
Valid Phone Number ID
Supported destination number
Appropriate Vapi subscription
✅ Current Architecture Status

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

The complete infrastructure pipeline successfully returns:

HTTP 200 OK

This verifies that:

Pub/Sub messages reach Cloud Run
OIDC authentication works
Cloud Run processes the webhook
FastAPI decodes the incident
Severity filtering works
The dispatch workflow executes successfully
🔮 Future Improvements
👨‍💻 On-Call Engineer Integration

The current implementation uses a configured engineer phone number.

A production-ready version should integrate with an on-call management system.

Example:

Critical Incident
       │
       ▼
Determine Affected Service
       │
       ▼
Query On-Call Schedule
       │
       ▼
Find Current On-Call Engineer
       │
       ▼
Initiate Voice Call

Possible integrations:

Splunk On-Call
PagerDuty
Opsgenie
Custom On-Call Database

This would ensure that only the engineer currently responsible for the affected service receives the incident call.

🔁 Escalation Policies

Future escalation logic could work like this:

Primary On-Call Engineer
          │
          ▼
     Voice Call
          │
     No Response
          │
          ▼
Secondary Engineer
          │
          ▼
     Voice Call
          │
     No Response
          │
          ▼
Engineering Manager
📞 Multi-Level Incident Escalation

Future versions could support:

CRITICAL
    ↓
Primary On-Call

No Response
    ↓
Secondary On-Call

No Response
    ↓
Incident Commander
Other Improvements
Cloud Monitoring alert integration
Automatic incident creation
Incident database storage
Retry policies for failed voice dispatches
Dead-letter Pub/Sub queues
Multiple SRE escalation contacts
Service ownership mapping
On-call schedule integration
SMS notifications
Slack notifications
Microsoft Teams notifications
Real production Vapi calling
Terraform infrastructure deployment
CI/CD with GitHub Actions
Kubernetes incident support
Automated remediation workflows
AI-generated incident summaries
💡 Potential Production Architecture

A production-ready version could look like:

Cloud Monitoring
       │
       ▼
Pub/Sub
       │
       ▼
Incident Dispatcher
       │
       ▼
Service Ownership Lookup
       │
       ▼
On-Call Management Platform
       │
       ▼
Current On-Call Engineer
       │
       ▼
AI Voice Agent
       │
       ├───────────────┐
       ▼               ▼
 Acknowledge      Trigger Action
       │               │
       ▼               ▼
Incident DB     Cloud Run / GCP API
🔍 How This Differs From Splunk On-Call or PagerDuty

Enterprise platforms already provide:

On-call scheduling
Escalation policies
Incident management
Notifications
Rotations
Incident tracking

This project focuses on a different technical problem:

Building a custom cloud-native incident automation workflow and connecting infrastructure failures directly to AI-powered voice interactions.

The goal is to demonstrate:

Event-driven architecture
Cloud-native development
Pub/Sub messaging
Cloud Run deployment
IAM and OIDC authentication
Secure webhook design
AI voice integration
Function calling
Incident automation
🧠 Key Learnings Demonstrated

This project demonstrates knowledge of:

Backend Engineering
FastAPI
Async Python
API integrations
Webhooks
Environment configuration
Google Cloud
Cloud Run
Cloud Pub/Sub
IAM
Service Accounts
OIDC authentication
Cloud Build
SRE Concepts
Incident response
Alert severity filtering
Escalation workflows
Service ownership
On-call engineering
Event-driven systems
AI Integration
AI voice agents
Function calling
AI-powered incident interaction
Automated operational workflows
👨‍💻 Author

Saran Kumar

Built as a cloud-native SRE automation and AI-powered incident response project.

📌 Project Status

🟢 Pub/Sub integration tested

🟢 Cloud Run deployment tested

🟢 OIDC authentication tested

🟢 Alert processing tested

🟢 Severity filtering tested

🟢 Simulation voice dispatch tested

🟢 Vapi tool endpoint tested

🟡 Real production voice calling depends on Vapi phone number and subscription support

🔮 On-call management integration planned

⭐ Future Vision

The long-term goal is to evolve this project into an intelligent incident response platform that can:

Detect critical cloud incidents
Identify the affected service
Determine the responsible on-call engineer
Initiate AI-powered voice escalation
Allow engineers to acknowledge incidents by voice
Trigger approved remediation actions
Escalate automatically when no response is received
Detect
   ↓
Understand
   ↓
Find On-Call Engineer
   ↓
Call
   ↓
Acknowledge
   ↓
Remediate
   ↓
Escalate if Required

⭐ If you found this project useful, consider starring the repository.


This version is **honest about the current state** of the project, while also showing a strong production vision. It doesn't falsely claim that real voice calls are currently working, and the **on-call engineer integration** makes the future architecture much more realistic. 