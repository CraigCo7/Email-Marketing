from google.cloud import spanner


class Account:
    def __init__(self, id, email, auth_type, password, account_name, status, more_info, created_by, updated_by, version):
        self.id = id
        self.email = email
        self.auth_type = auth_type
        self.password = password
        self.account_name = account_name
        self.status = status
        self.more_info = more_info
        self.created_at = spanner.COMMIT_TIMESTAMP
        self.updated_at = spanner.COMMIT_TIMESTAMP
        self.created_by = created_by
        self.updated_by = updated_by
        self.version = version

    def __repr__(self):

        return (f"""Account(id={self.id}, email={self.email}, auth_type={self.auth_type}, password={self.password},
                account_name={self.account_name}, status={self.status}, more_info={self.more_info},
                created_at={self.created_at}, updated_at={self.updated_at}, created_by={self.created_by},
                updated_by={self.updated_by}, version={self.version})""")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "auth_type": self.auth_type,
            "password": self.password,
            "account_name": self.account_name,
            "status": self.status,
            "more_info": self.more_info,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "version": self.version
        }


def create_table(database):
    # Check if the table already exists
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT table_name FROM information_schema.tables WHERE table_name = 'account'"
        )
        table_exists = any(row for row in results)

    if table_exists:
        print("Account table already exists. Skipping creation.")
        return

    # DDL statement to create the table
    ddl_statements = [
        """
        CREATE TABLE account (
            id STRING(MAX) NOT NULL,
            email STRING(MAX) NOT NULL,
            auth_type STRING(MAX) NOT NULL,
            password STRING(MAX) NOT NULL,
            account_name STRING(MAX),
            status STRING(MAX) NOT NULL,
            more_info JSON NOT NULL,
            created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
            updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
            created_by STRING(MAX) NOT NULL,
            updated_by STRING(MAX) NOT NULL,
            version INT64 NOT NULL
        ) PRIMARY KEY (id)
        """
    ]

    # Apply the DDL statement to create the table
    operation = database.update_ddl(ddl_statements)
    print("Waiting for operation to complete...")
    operation.result()
    print("Account table created successfully.")


def insert_single_entry(database, account: Account):
    with database.batch() as batch:
        batch.insert(
            table='account',
            columns=(
                'id', 'email', 'auth_type', 'password', 'account_name', 'status',
                'more_info', 'created_at', 'updated_at', 'created_by', 'updated_by', 'version'
            ),
            values=[
                (
                    account.id, account.email, account.auth_type, account.password, account.account_name, account.status,
                    account.more_info, account.created_at, account.updated_at,
                    account.created_by, account.updated_by, account.version
                ),
            ]
        )
    print("Single entry inserted successfully.")


def insert_bulk_entries(database, accounts):
    with database.batch() as batch:
        batch.insert(
            table='account',
            columns=(
                'id', 'email', 'auth_type', 'password', 'account_name', 'status',
                'more_info', 'created_at', 'updated_at', 'created_by', 'updated_by', 'version'
            ),
            values=[
                (
                    account.id, account.email, account.auth_type, account.password, account.account_name, account.status,
                    account.more_info, account.created_at, account.updated_at,
                    account.created_by, account.updated_by, account.version
                )
                for account in accounts
            ]
        )
    print("Bulk entries inserted successfully.")


def read_all_entries(database):
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql("SELECT * FROM account")
        accounts = []
        for row in results:
            account = Account(
                id=row[0],
                email=row[1],
                auth_type=row[2],
                password=row[3],
                account_name=row[4],
                status=row[5],
                more_info=row[6],
                created_by=row[9],
                updated_by=row[10],
                version=row[11]
            )
            account.created_at = row[7]
            account.updated_at = row[8]
            accounts.append(account)
            print(account)

        return accounts

# Function to populate the database with test entries


def populate_test_entries(database):
    create_table(database)
    bulk_accounts = [
        Account(
            '1', 'example@example.com', 'password', 'example_password', 'Example Name', 'active',
            '{"info": "more details"}', 'creator', 'updater', 1
        ),
        Account(
            '2', 'user1@example.com', 'password', 'password1', 'User One', 'active',
            '{"info": "details 1"}', 'creator', 'updater', 1
        ),
        Account(
            '3', 'user2@example.com', 'password', 'password2', 'User Two', 'active',
            '{"info": "details 2"}', 'creator', 'updater', 1
        ),
        # Add more entries as needed
    ]

    insert_bulk_entries(database, bulk_accounts)
    print("Database populated with test entries successfully.")
