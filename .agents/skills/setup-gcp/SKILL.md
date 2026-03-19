---
name: setup-gcp
description: "Guide the setup and credential management for GCP services like Firestore, GenAI, and TTS in TypeScript environments. Use this skill when asked to 'setup firestore', 'configure gcp credentials', 'connect to google cloud', or similar GCP setup tasks."
---

# Setup GCP Services

Follow this hybrid setup process to seamlessly support both local development (via standard `gcloud` auth) and production (via `.env` variables) without rewriting code.

## 1. Setup Environment Variables

For production (or local overrides), store the **entire JSON string** of your single unified GCP Service Account key inside `.env` (or `.env.local` for Next.js):

```env
GOOGLE_CLOUD_CREDENTIALS={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"..."}
```

## 2. Local Terminal Auth (Fallback)

If `GOOGLE_CLOUD_CREDENTIALS` is omitted during local development, the SDK falls back to Application Default Credentials (ADC). Authenticate locally via:

```bash
gcloud auth application-default login
```

_(Confused about the difference between `gcloud auth login` and `application-default login`? Read [references/Local-Gcloud-Auth.md](references/Local-Gcloud-Auth.md))_

## 3. Implementation Pattern

Initialize your GCP clients (Firestore, TTS, etc.) using this exact conditional pattern. It parses the `.env` if it exists, otherwise falls back neatly to ADC:

```typescript
import { Firestore } from "@google-cloud/firestore";

const firestoreConfig: any = {};

if (process.env.GOOGLE_CLOUD_CREDENTIALS) {
  const credentials = JSON.parse(process.env.GOOGLE_CLOUD_CREDENTIALS);
  firestoreConfig.projectId = credentials.project_id;
  firestoreConfig.credentials = {
    client_email: credentials.client_email,
    private_key: credentials.private_key?.replace(/\\n/g, "\n"),
  };
}

const db = new Firestore(firestoreConfig);
```

## Gotchas

- **Double-Escaped Newlines**: Hosting providers (like Vercel) often double-escape newlines in the `private_key` JSON property. Always run `.replace(/\\n/g, "\n")` before passing it to the SDK.
- **Client-Side Exposure**: Do **not** prefix the variable with `NEXT_PUBLIC_`. GCP Credentials must _never_ reach the browser. Scope usage entirely to App Router API routes or Server Actions.

---

## IAM & Service Account Knowledge Base

If you need deeper historical context on Google Cloud Service Accounts, the difference between the IAM page and the Service Accounts page, or the history/warnings of the `firebase-adminsdk` god-mode account, please read:
[references/IAM-and-Service-Accounts.md](references/IAM-and-Service-Accounts.md)

---

## Troubleshooting Checklist

### Fix `Error 7: PERMISSION_DENIED`

If the Service Account authenticates correctly but lacks the specific role needed for the action, run this validation loop:

- [ ] 1. Check your `.env.local` to find the exact `"client_email"` being used.
- [ ] 2. Open Google Cloud Console and navigate to **IAM & Admin > IAM**.
- [ ] 3. Click **Grant Access** (or edit the user if they already exist on the list).
- [ ] 4. Paste the exact `"client_email"`.
- [ ] 5. Assign the necessary role (e.g., `Cloud Datastore User` for Firestore reads/writes, or `Cloud Text-to-Speech Client` for TTS).
- [ ] 6. Wait exactly 60 seconds (IAM changes take time to propagate globally).
- [ ] 7. Retry the request.
