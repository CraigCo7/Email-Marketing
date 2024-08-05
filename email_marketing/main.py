import os
from google.cloud import spanner
from flask import Flask, request
from dotenv import load_dotenv

from .account import populate_test_entries as populate_account_entries
from .account import read_all_entries as read_all_account_entries
from .user_feedback import populate_test_entries as populate_user_feedback_entries
from .user_feedback import read_all_entries as read_all_user_feedback_entries
from .email_marketing import read_all_entries as read_all_email_marketing_entries
from .email_marketing import truncate_table
from .email_marketing import update_email_marketing

load_dotenv()

# Set the Spanner emulator host and disable credentials
os.environ["SPANNER_EMULATOR_HOST"] = os.getenv("SPANNER_EMULATOR_HOST")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
os.environ["SPANNER_EMULATOR_CREDENTIALS"] = os.getenv(
    "SPANNER_EMULATOR_CREDENTIALS")

# Initialize the Spanner client
spanner_client = spanner.Client()

# Define the instance and database
instance_id = 'test-instance'
database_id = 'test-database'
instance = spanner_client.instance(instance_id)
database = instance.database(database_id)


# Initialize the Flask app
app = Flask(__name__)


@app.route('/update_email_marketing', methods=['POST'])
def update_email_marketing_route():
    return update_email_marketing(database)


if __name__ == '__main__':
    if read_all_account_entries(database) == None:
        populate_account_entries(database)
    if read_all_user_feedback_entries(database) == None:
        populate_user_feedback_entries(database)
    app.run(port=8080, debug=True)

# curl -X POST http://localhost:8080/update_email_marketing


# Cron jobs

# gcloud functions deploy populate_email_marketing \
#     - -runtime python39 \
#     - -trigger-http \
#     - -allow-unauthenticated \
#     - -entry-point populate_email_marketing_route

# gcloud scheduler jobs create http daily-populate-email-marketing \
#     - -schedule = "0 0 * * *" \
#     - -uri = "https://REGION-PROJECT_ID.cloudfunctions.net/populate_email_marketing" \
#     - -http-method = POST \
#     - -time-zone = "YOUR_TIME_ZONE"
