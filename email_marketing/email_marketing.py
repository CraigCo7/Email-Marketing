from google.cloud import spanner
import uuid


class EmailMarketing:
    def __init__(self, id, email, first_name, last_name, source_table, source_id, opt_in_status):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.source_table = source_table
        self.source_id = source_id
        self.opt_in_status = opt_in_status
        self.created_at = spanner.COMMIT_TIMESTAMP
        self.updated_at = spanner.COMMIT_TIMESTAMP

    def __repr__(self):
        return (f"""EmailMarketing(id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name},
                source_table={self.source_table}, source_id={self.source_id}, opt_in_status={self.opt_in_status},
                created_at={self.created_at}, updated_at={self.updated_at})""")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "source_table": self.source_table,
            "source_id": self.source_id,
            "opt_in_status": self.opt_in_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def get_email(self):
        return self.email

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name


# Method to create the table


def create_table(database):
    # Check if the table already exists
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT table_name FROM information_schema.tables WHERE table_name = 'email_marketing'"
        )
        table_exists = any(row for row in results)

    if table_exists:
        print("EmailMarketing table already exists. Skipping creation.")
        return

    # DDL statement to create the table
    ddl_statements = [
        """
        CREATE TABLE email_marketing (
            id STRING(50) NOT NULL,
            email STRING(1024) NOT NULL,
            first_name STRING(256),
            last_name STRING(256),
            source_table STRING(50) NOT NULL,
            source_id STRING(50) NOT NULL,
            opt_in_status BOOL NOT NULL,
            created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
            updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
        ) PRIMARY KEY (id)
        """
    ]

    # Apply the DDL statement to create the table
    operation = database.update_ddl(ddl_statements)
    print("Waiting for operation to complete...")
    operation.result()
    print("EmailMarketing table created successfully.")

# Method to insert a single entry


def insert_single_entry(database, email_marketing: EmailMarketing):
    with database.batch() as batch:
        batch.insert(
            table='email_marketing',
            columns=(
                'id', 'email', 'first_name', 'last_name', 'source_table', 'source_id', 'opt_in_status',
                'created_at', 'updated_at'
            ),
            values=[
                (
                    email_marketing.id, email_marketing.email, email_marketing.first_name, email_marketing.last_name,
                    email_marketing.source_table, email_marketing.source_id, email_marketing.opt_in_status,
                    email_marketing.created_at, email_marketing.updated_at
                ),
            ]
        )
    print("Single entry inserted successfully.")

# Method to insert bulk entries


def insert_bulk_entries(database, email_marketing_list):
    with database.batch() as batch:
        batch.insert(
            table='email_marketing',
            columns=(
                'id', 'email', 'first_name', 'last_name', 'source_table', 'source_id', 'opt_in_status',
                'created_at', 'updated_at'
            ),
            values=[
                (
                    generate_unique_id(), email_marketing.email, email_marketing.first_name, email_marketing.last_name,
                    email_marketing.source_table, email_marketing.source_id, email_marketing.opt_in_status,
                    email_marketing.created_at, email_marketing.updated_at
                )
                for email_marketing in email_marketing_list
            ]
        )
    print("Bulk entries inserted successfully.")

# Method to read all entries


def get_all_entries(database):
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql("SELECT * FROM email_marketing")
        email_marketing_list = []
        for row in results:
            email_marketing = EmailMarketing(
                id=row[0],
                email=row[1],
                first_name=row[2],
                last_name=row[3],
                source_table=row[4],
                source_id=row[5],
                opt_in_status=row[6]
            )
            email_marketing.created_at = row[7]
            email_marketing.updated_at = row[8]
            email_marketing_list.append(email_marketing)

        return email_marketing_list


def read_all_entries(database):
    entries = get_all_entries(database)
    print(entries)


def update_opt_in_status(database, id, new_status):
    with database.batch() as batch:
        batch.update(
            table='email_marketing',
            columns=('id', 'opt_in_status', 'updated_at'),
            values=[(id, new_status, spanner.COMMIT_TIMESTAMP)]
        )
    print(f"Opt-in status for entry with ID {id} updated successfully.")


def truncate_table(database):
    with database.batch() as batch:
        batch.delete(
            table='email_marketing',
            keyset=spanner.KeySet(all_=True)
        )
    print("EmailMarketing table emptied successfully.")


def generate_unique_id():
    return str(uuid.uuid4())


def update_email_marketing(database):
    existing_emails = set()

    # Fetch existing emails from email_marketing table
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql("SELECT email FROM email_marketing")
        for row in results:
            existing_emails.add(row[0])

    new_entries = []

    # Traverse user_feedback table
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT id, email, username, full_name FROM user_feedback WHERE email IS NOT NULL")
        for row in results:
            if row[1] not in existing_emails:
                new_entry = EmailMarketing(
                    id=row[0],
                    email=row[1],
                    first_name=row[2].split()[0] if row[2] else None,
                    last_name=row[2].split()[-1] if row[2] else None,
                    source_table='user_feedback',
                    source_id=row[0],
                    opt_in_status=True  # Assuming opt-in status is true for this example
                )
                new_entries.append(new_entry)
                existing_emails.add(row[1])

    # Traverse account table
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT id, email, account_name FROM account WHERE email IS NOT NULL")
        for row in results:
            if row[1] not in existing_emails:
                new_entry = EmailMarketing(
                    id=row[0],
                    email=row[1],
                    first_name=row[2].split()[0] if row[2] else None,
                    last_name=row[2].split()[-1] if row[2] else None,
                    source_table='account',
                    source_id=row[0],
                    opt_in_status=True  # Assuming opt-in status is true for this example
                )
                new_entries.append(new_entry)
                existing_emails.add(row[1])

    # Insert new entries into email_marketing table
    if new_entries:
        insert_bulk_entries(database, new_entries)
        print(f"{len(new_entries)} new entries added to email_marketing table.")
    else:
        print("No new entries to add.")

    return "Test Success"
