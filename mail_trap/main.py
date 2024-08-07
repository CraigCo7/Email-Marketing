from typing import List
import mailtrap as mt
import os
from dotenv import load_dotenv
from google.cloud import spanner
from email_records.email_record import EmailRecord

from email_records.email_record import get_all_entries as get_all_email_marketing_entries
load_dotenv()

# Set the Spanner emulator host and disable credentials
os.environ["SPANNER_EMULATOR_HOST"] = os.getenv("SPANNER_EMULATOR_HOST")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
os.environ["SPANNER_EMULATOR_CREDENTIALS"] = os.getenv(
    "SPANNER_EMULATOR_CREDENTIALS")

# Initialize the Spanner client
spanner_client = spanner.Client()

# Define the instance and database
instance_id = os.getenv("INNOSEARCH_SPANNER_INSTANCE_ID")
innosearch_prod_database_id = os.getenv("INNOSEARCH-PROD_DB_ID")
innosearch_auth_prod_database_id = os.getenv("INNOSEARCH-AUTH-PROD_DB_ID")

instance = spanner_client.instance(instance_id)

innosearch_prod_database = instance.database(innosearch_prod_database_id)
innosearch_auth_prod_database = instance.database(
    innosearch_auth_prod_database_id)


def transactional_stream(email_list: List[EmailRecord]):

    client = mt.MailtrapClient(token=os.getenv("MAILTRAP_API_TOKEN"))

    for item in email_list:
        mail = mt.MailFromTemplate(
            sender=mt.Address(email="craigco@innosearch.ai",
                              name="Mailtrap Test"),
            to=[mt.Address(email=item.email), mt.Address(
                email="craigco@innosearch.ai")],
            template_uuid="2a800b7f-ef5d-4d8f-8cf6-c1a119d66c29",
            template_variables={"name": item.first_name},
        )

        response = client.send(mail)
        if response["success"]:
            print(f"Email sent to {item.email}")
        else:
            print(f"Failed to send email to {item.email}")


def bulk_stream(email_list: List[EmailRecord]):
    # create mail object
    mail = mt.MailFromTemplate(
        sender=mt.Address(email="craigco@innosearch.ai", name="Mailtrap Test"),
        to=[mt.Address(email=item.email) for item in email_list],
        template_uuid="7755f2f7-b76c-47b8-b71a-55316fd6c54a",
        # template_variables={},
    )

    # create client and send
    client = mt.MailtrapClient(token=os.getenv("MAILTRAP_API_TOKEN"))
    client.send(mail)


if __name__ == '__main__':
    emails = get_all_email_marketing_entries(innosearch_prod_database)
    transactional_stream(emails)
