from typing import List
import mailtrap as mt
import os
from dotenv import load_dotenv
from google.cloud import spanner
from email_marketing.email_marketing import EmailMarketing

from email_marketing.email_marketing import get_all_entries as get_all_email_marketing_entries
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


def transactional_stream(email_list: List[EmailMarketing]):

    client = mt.MailtrapClient(token=os.getenv("MAILTRAP_API_TOKEN"))

    for item in email_list:
        mail = mt.MailFromTemplate(
            sender=mt.Address(email="craigco@innosearch.ai",
                              name="Mailtrap Test"),
            to=[mt.Address(email=item.email)],
            template_uuid="7755f2f7-b76c-47b8-b71a-55316fd6c54a",
            template_variables={"name": item.first_name},
        )

        response = client.send(mail)
        if response["success"]:
            print(f"Email sent to {item.email}")
        else:
            print(f"Failed to send email to {item.email}")


def bulk_stream(email_list: List[EmailMarketing]):
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
    emails = get_all_email_marketing_entries(database)
    transactional_stream(emails)
