# IAM & Service Account Deep Dive

This reference document expands on the core Service Account and IAM principles detailed in the main `SKILL.md`. Load this file when you need deeper context on why certain permissions exist, how Google structures Service Accounts natively, or how to design permissions for scaled services.

## Service Accounts vs. User Accounts

A **Service Account** is essentially a "robot user" that lives inside your project. When an application runs server-side (like a Next.js API route), it must authenticate as one of these robot users, not as your personal Google account.

By default, a newly created Service Account has zero permissions. You must explicitly grant the robot permission to interact with specific GCP resources using IAM roles.

## Identifying Account Types

When managing accounts in the Google Cloud Console, you will encounter three primary types of accounts/agents:

### 1. Unified Application Service Accounts (The Standard)
* **Format:** Custom names like `nextjs-server-sa@your-project.iam.gserviceaccount.com`
* **Purpose:** Created manually by you to act as the single identity for your application.
* **Usage:** For monolithic apps (like a standard Next.js deployment), one account should be granted all necessary application roles (e.g., `Cloud Datastore User`, `Cloud Text-to-Speech Client`) to limit the number of `.env` credentials you must manage.

### 2. The `firebase-adminsdk` Account (God-Mode)
* **Format:** `firebase-adminsdk-fbsvc@your-project.iam.gserviceaccount.com`
* **Purpose:** Automatically created when a GCP project is upgraded to standard Firebase. It is granted the `Firebase Admin SDK Administrator Service Agent` role.
* **Usage:** **Do not use this account for standard GCP APIs.** It is exclusively intended for the `firebase-admin` Node.js SDK to bypass all security rules (e.g., manually resetting user passwords, wiping Realtime Databases, or sending bulk Push Notifications). Using it for simple Firestore reads/writes or TTS is dangerous and violates the principle of least privilege.

### 3. Google Service Agents (Hidden Robots)
* **Format:** `service-[project-number]@gcp-sa-[service].iam.gserviceaccount.com`
* **Purpose:** Google's internal robots used to make its own services talk to each other across the cloud infrastructure.
* **Visibility:** These are hidden by default on the IAM page. You must click the **"Include Google-provided role grants"** checkbox to view them. They should never be modified, and you should never download JSON keys for them.

## Google Cloud Console Layout Quirks

Navigating Google Cloud Console can be confusing because the "IAM" page and the "Service Accounts" page serve completely different functions:

* **IAM Page = The Role Map**: The "IAM" (Identity and Access Management) page only displays users or service accounts that have been *explicitly granted project-level roles*. If you create a brand new Service Account with zero permissions (or if it only has localized permissions on a specific bucket or resource), it will likely not show up on the main IAM page.
* **Service Accounts Page = The Master List**: To see every single trackable service account created within your project, navigate specifically to **IAM & Admin > Service Accounts**. 

## Microservices vs. Monolithic Approaches

* **Monolithic Approach (Recommended for Next.js)**: Create one primary service account (e.g., `nextjs-server-sa@...`) and grant it all roles required by your application. Use this single credentials string in your `.env`.
* **Microservices Approach**: Strictly separate service accounts when you have completely separate deployments or workers. For example, if a separate Python worker handles a specific parsing queue, give it a unique `data-parser-sa` account with strictly limited write permissions. This ensures that if the Python server is compromised, the attacker cannot leverage it to start generating expensive Text-to-Speech audio on your dime.
