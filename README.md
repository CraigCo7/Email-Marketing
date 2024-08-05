# Repository Responsibilities

1. Daily fetching unique emails from the `account` table in the `innosearch-auth-prod` database and adding them to a separate table (`EmailMarketing`).
2. Daily fetching unique emails from the `user_feedback` table in the `innosearch-prod` database and adding them to a separate table (`EmailMarketing`).
3. Sending emails to these email addresses using the Mailtrap API.

## What it does

1. Recreates 2 local tables that mimic the schemas of the `account` and `user_feedback` tables, and populates them with sample entries
2. Creates a new table to store the information (`EmailMarketing`).
3. Sends an email to them, using a template created on mailtrap.

## Requirements

- Docker
- Python
- GCloud CLI

## Setup

### Set up Local Spanner Emulator

1. **Upgrade pip**:

   ```sh
   python3 -m pip install --upgrade pip
   pip --version
   ```

2. **Install virtualenv**:

   ```sh
   pip install virtualenv
   ```

3. **Set Python version to use**:

   ```sh
   VERSION="3.9"
   ```

4. **Create a virtual environment**:

   ```sh
   python3 -m virtualenv --python=python$VERSION .venv
   ```

5. **Activate environment and install dependency libraries**:

   ```sh
   source .venv/bin/activate
   ```

6. **Pull emulator image**:

   ```sh
   docker pull gcr.io/cloud-spanner-emulator/emulator
   ```

7. **Start Cloud Spanner Emulator**:
   ```sh
   docker run -p 9010:9010 -p 9020:9020 gcr.io/cloud-spanner-emulator/emulator
   ```

### GCloud Authenticate and Start Emulator

1. **Update GCloud components**:

   ```sh
   gcloud components update
   ```

2. **Authenticate login**:

   ```sh
   gcloud auth login
   ```

3. **Start Cloud Spanner Emulator**:
   ```sh
   gcloud emulators spanner start
   ```

# Running the program

1. **Create Dummy Tables + Data**:
   **Eventually when we move this off local emulator to the cloud, this will no longer be needed.**
   ```sh
    python -m email_marketing.main
   ```

- this also creates a docker container so we can run cloud functions (when we eventually use cloud scheduler)

2. **Run the cloud function to retrieve new emails**:
   ```sh
   curl -X POST http://localhost:8080/update_email_marketing
   ```
3. **Run the program to send the emails**
   ```sh
   python -m mail_trap.main
   ```
