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

5. **Install necessary packages**:

   ```sh
   pip install google-cloud-spanner
   pip install flask
   pip install python-dotenv
   pip install mailtrap
   ```

6. **Activate environment and install dependency libraries**:

   ```sh
   source .venv/bin/activate
   ```

7. **Pull emulator image**:

   ```sh
   docker pull gcr.io/cloud-spanner-emulator/emulator
   ```

8. **Start Cloud Spanner Emulator**:
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
4. **Configure GCloud**:

   ```sh
   # Configure Cloud Spanner endpoint, project and disable authentication
    gcloud config configurations create emulator
    # gcloud config configurations activate emulator
    gcloud config set auth/disable_credentials true
    gcloud config set project test-project
    gcloud config set api_endpoint_overrides/spanner http://localhost:9020/
   ```

5. **Create a Cloud Spanner Instance & Databases**:

   ```sh
   gcloud spanner instances create test-instance --config=emulator-config --description=”Test Instance” --nodes=1
   gcloud spanner databases create innosearch-auth-prod --instance test-instance
   gcloud spanner databases create innosearch-prod --instance test-instance
   ```

# Running the program

1. **Create Dummy Tables + Data**:
   **Eventually when we move this off local emulator to the cloud, this will no longer be needed.**
   ```sh
    python -m email_records.populate_tables
    python -m email_records.main
   ```

- this also creates a docker container so we can run cloud functions (when we eventually use cloud scheduler)

2. **Run the cloud function to retrieve new emails**:
   ```sh
   curl -X POST http://localhost:8080/update_email_records
   ```
3. **Run the program to send the emails**
   ```sh
   python -m mail_trap.main
   ```
