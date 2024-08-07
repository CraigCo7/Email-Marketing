import os
from google.cloud import spanner
from .account import populate_test_entries as populate_account_table
from .user_feedback import populate_test_entries as populate_user_feedback_table
from .email_record import create_table as create_email_record_table
from dotenv import load_dotenv

load_dotenv()


instance_id = os.getenv("INNOSEARCH_SPANNER_INSTANCE_ID")
innosearch_prod_database_id = os.getenv("INNOSEARCH-PROD_DB_ID")
innosearch_auth_prod_database_id = os.getenv("INNOSEARCH-AUTH-PROD_DB_ID")

# Initialize the Spanner client
spanner_client = spanner.Client()

instance = spanner_client.instance(instance_id)

innosearch_prod_database = instance.database(innosearch_prod_database_id)
innosearch_auth_prod_database = instance.database(
    innosearch_auth_prod_database_id)

if __name__ == '__main__':
    create_email_record_table(innosearch_prod_database)
    populate_account_table(innosearch_auth_prod_database)
    populate_user_feedback_table(innosearch_prod_database)
