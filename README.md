# 🚨 GCP SRE Voice Dispatcher

An AI-powered Site Reliability Engineering (SRE) incident response system that receives Google Cloud alerts via Pub/Sub and automatically triggers a voice-based escalation workflow.

Designed specifically for monitoring and responding to critical failures involving **Google Cloud Run services and jobs**, this system processes high-severity incidents and initiates an automated voice escalation workflow, reducing the reliance on manual dashboard monitoring.

> **⚠️ Note on Production Use:** The project currently supports a fully tested simulation workflow. Real production voice calling depends on Vapi account configuration, supported phone numbers, and active subscription capabilities.

---

## ✨ Overview

The system processes critical infrastructure alerts through the following event-driven pipeline:

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
```

### 🎯 Why This Project?

Modern SRE teams rely on enterprise incident management platforms like PagerDuty, Splunk On-Call, or Opsgenie. This project is not intended to replace those tools. Instead, it serves as a proof-of-concept demonstrating how engineers can build custom, cloud-native incident automation workflows bridging cloud infrastructure failures and AI-powered voice interactions using **Google Cloud, Pub/Sub, Cloud Run, FastAPI, and Vapi Function Calling**.

### 🚀 Features

*   **Google Cloud Native:** Receives incident alerts directly through Google Cloud Pub/Sub.
*   **Targeted Monitoring:** Supports Cloud Run services and jobs.
*   **Intelligent Filtering:** Filters incidents based on severity, escalating only `CRITICAL`, `ERROR`, and `P0` alerts.
*   **Secure Architecture:** Validates Pub/Sub push messages using OIDC authentication.
*   **Dual-Mode Dispatch:** 
    *   *Simulation Mode:* For end-to-end testing without triggering external calls.
    *   *Production Mode:* Integrates with Vapi for live voice dispatch.
*   **Interactive Voice Tools:** Provides Vapi tool endpoints allowing the AI assistant to acknowledge incidents dynamically.
*   **Cloud Run Ready:** Containerized and optimized for serverless deployment with detailed application logging.

---

## 🛠 Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, HTTPX |
| **Google Cloud** | Cloud Run, Cloud Pub/Sub, Cloud IAM, Cloud Build |
| **AI & Voice** | Vapi, AI Voice Assistant, Function Calling |
| **Infrastructure** | Docker, Google Cloud CLI |

---

## 📁 Project Structure

```text
gcp-sre-voice-dispatcher/
├── app/
│   ├── api/
│   │   └── vapi_tools.py
│   ├── models/
│   │   └── alerts.py
│   ├── security/
│   │   └── auth.py
│   ├── services/
│   │   └── vapi_service.py
│   ├── config.py
│   └── main.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💻 Local Setup

### 1. Prerequisites

*   Python 3.11+
*   Google Cloud SDK & active GCP Project (with Cloud Run and Pub/Sub APIs enabled)
*   Docker
*   Vapi account, API key, Assistant ID, and provisioned phone number (for Production Mode)

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
git clone <YOUR_REPOSITORY_URL>
cd gcp-sre-voice-dispatcher
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
VAPI_API_KEY=your_vapi_api_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
ENGINEER_PHONE_NUMBER=+1234567890
INTERNAL_SECRET_TOKEN=your_secret_token
DISPATCH_MODE=simulation
```

### 4. Running Locally

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```
Test the health endpoint: `curl http://127.0.0.1:8000/health`

---

## ⚙️ Dispatch Modes

### 🧪 Simulation Mode (`DISPATCH_MODE=simulation`)
Recommended for local development, CI/CD testing, and infrastructure demonstrations. No real phone call is made. The system simulates the voice dispatch and logs the incident.

```json
{
  "status": "call_initiated",
  "incident_id": "simulation-test-001",
  "resource": "sre-test-job"
}
```

### 📞 Production Mode (`DISPATCH_MODE=production`)
Sends an outbound call request to the Vapi API. Requires a valid Vapi API key, Assistant ID, Phone Number ID, and a subscription supporting outbound/international calling to the target engineer's number. 

*Note: Free Vapi numbers do not support international calls. Ensure your Vapi plan aligns with the on-call engineer's location.*

---

## ☁️ Google Cloud Deployment

Set your Google Cloud project and enable APIs:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com pubsub.googleapis.com cloudbuild.googleapis.com
```

### 1. Create Pub/Sub Topic
```bash
gcloud pubsub topics create gcp-sre-alerts
```

### 2. Deploy to Cloud Run
```bash
gcloud run deploy gcp-sre-voice-dispatcher   --source .   --region asia-south1   --project YOUR_PROJECT_ID   --allow-unauthenticated   --update-env-vars "DISPATCH_MODE=simulation"
```

### 3. Security & IAM

Create a dedicated service account for Pub/Sub push delivery:
```bash
gcloud iam service-accounts create pubsub-push-dispatcher   --display-name="Pub/Sub Push Dispatcher"   --project YOUR_PROJECT_ID
```

Grant the service account Cloud Run Invoker permissions:
```bash
gcloud run services add-iam-policy-binding gcp-sre-voice-dispatcher   --region asia-south1   --project YOUR_PROJECT_ID   --member="serviceAccount:pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com"   --role="roles/run.invoker"
```

Allow Pub/Sub to generate OIDC tokens (Replace `PROJECT_NUMBER`):
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID   --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com"   --role="roles/iam.serviceAccountTokenCreator"
```

### 4. Create Pub/Sub Push Subscription
Link the topic to your Cloud Run endpoint:
```bash
gcloud pubsub subscriptions create gcp-sre-alerts-push   --topic=gcp-sre-alerts   --push-endpoint="https://YOUR_CLOUD_RUN_URL/webhook/pubsub-alert"   --push-auth-service-account="pubsub-push-dispatcher@YOUR_PROJECT_ID.iam.gserviceaccount.com"   --project=YOUR_PROJECT_ID
```

---

## 🛠 Vapi Tool Endpoints (Function Calling)

The application provides a webhook endpoint (`POST /webhook/vapi-tools`) that the Vapi voice assistant can query during an active incident call to execute backend actions, such as acknowledging the incident.

**Example Tool Request from Vapi:**
```json
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
```

---

## 🔮 Future Vision & Architecture

While the current implementation relies on a statically configured engineer phone number, the roadmap includes building an intelligent incident response platform mirroring enterprise capabilities.

### Planned Enhancements
*   **On-Call Engineer Integration:** Dynamically query schedules (PagerDuty, Splunk On-Call) to route calls to the active primary engineer based on specific service ownership.
*   **Multi-Level Escalation:** Implement fallback logic: Primary On-Call ➔ Secondary On-Call ➔ Incident Commander.
*   **Automated Remediation:** Allow the AI agent to trigger standard operating procedures (SOPs) or restart failed Cloud Run jobs directly via voice commands.
*   **Infrastructure as Code:** Migrate deployment steps to Terraform.
*   **Omnichannel Alerts:** Add fallback notifications via SMS, Slack, and Microsoft Teams.

### Project Status

*   🟢 Pub/Sub integration tested
*   🟢 Cloud Run deployment & OIDC authentication tested
*   🟢 Alert processing & severity filtering tested
*   🟢 Simulation voice dispatch & Vapi tool endpoints tested
*   🟡 Real production voice calling (Dependent on Vapi subscription capabilities)
*   🔮 On-call schedule integration (Planned)

**Author:** Saran Kumar  
*Built as a cloud-native SRE automation and AI-powered incident response proof-of-concept.*

⭐ If you found this project useful, consider starring the repository.