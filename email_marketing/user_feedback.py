from google.cloud import spanner


class UserFeedback:
    def __init__(self, id, feedback_type, creation_time, username, email, full_name, content, user_ip, user_agent):
        self.id = id
        self.feedback_type = feedback_type
        self.creation_time = creation_time
        self.username = username
        self.email = email
        self.full_name = full_name
        self.content = content
        self.user_ip = user_ip
        self.user_agent = user_agent

    def __repr__(self):
        return (f"""UserFeedback(id={self.id}, feedback_type={self.feedback_type}, creation_time={self.creation_time},
                username={self.username}, email={self.email}, full_name={self.full_name}, content={self.content},
                "user_ip={self.user_ip}, user_agent={self.user_agent})""")

    def to_dict(self):
        return {
            "id": self.id,
            "feedback_type": self.feedback_type,
            "creation_time": self.creation_time,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "content": self.content,
            "user_ip": self.user_ip,
            "user_agent": self.user_agent
        }


def create_table(database):
    # Check if the table already exists
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT table_name FROM information_schema.tables WHERE table_name = 'user_feedback'"
        )
        table_exists = any(row for row in results)

    if table_exists:
        print("Feedback table already exists. Skipping creation.")
        return

    # DDL statement to create the table
    ddl_statements = [
        """
        CREATE TABLE user_feedback (
            id STRING(50) NOT NULL,
            feedback_type STRING(20) NOT NULL,
            creation_time TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
            username STRING(100) NOT NULL,
            email STRING(1024) NOT NULL,
            full_name STRING(1024) NOT NULL,
            content STRING(8192) NOT NULL,
            user_ip STRING(256) NOT NULL,
            user_agent STRING(1024) NOT NULL
        ) PRIMARY KEY (id)
        """
    ]

    # Apply the DDL statement to create the table
    operation = database.update_ddl(ddl_statements)
    print("Waiting for operation to complete...")
    operation.result()
    print("Feedback table created successfully.")


def insert_single_entry(database, feedback: UserFeedback):
    with database.batch() as batch:
        batch.insert(
            table='user_feedback',
            columns=(
                'id', 'feedback_type', 'creation_time', 'username', 'email', 'full_name',
                'content', 'user_ip', 'user_agent'
            ),
            values=[
                (
                    feedback.id, feedback.feedback_type, feedback.creation_time, feedback.username,
                    feedback.email, feedback.full_name, feedback.content, feedback.user_ip, feedback.user_agent
                ),
            ]
        )
    print("Single entry inserted successfully.")


def insert_bulk_entries(database, feedback_list):
    with database.batch() as batch:
        batch.insert(
            table='user_feedback',
            columns=(
                'id', 'feedback_type', 'creation_time', 'username', 'email', 'full_name',
                'content', 'user_ip', 'user_agent'
            ),
            values=[
                (
                    feedback.id, feedback.feedback_type, feedback.creation_time, feedback.username,
                    feedback.email, feedback.full_name, feedback.content, feedback.user_ip, feedback.user_agent
                )
                for feedback in feedback_list
            ]
        )
    print("Bulk entries inserted successfully.")


def read_all_entries(database):
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql("SELECT * FROM user_feedback")
        feedback_list = []
        for row in results:
            feedback = UserFeedback(
                id=row[0],
                feedback_type=row[1],
                creation_time=row[2],
                username=row[3],
                email=row[4],
                full_name=row[5],
                content=row[6],
                user_ip=row[7],
                user_agent=row[8]
            )
            feedback_list.append(feedback)
            print(feedback)

        return feedback_list


# Function to populate the database with test entries


def populate_test_entries(database):
    create_table(database)
    bulk_feedback = [
        UserFeedback(
            id='1', feedback_type='bug', creation_time='2024-08-01T12:34:56Z', username='user1',
            email='user1@example.com', full_name='User One', content='There is a bug.',
            user_ip='192.168.1.1', user_agent='Mozilla/5.0'
        ),
        UserFeedback(
            id='2', feedback_type='feature', creation_time='2024-08-01T13:34:56Z', username='user2',
            email='user2@example.com', full_name='User Two', content='Please add this feature.',
            user_ip='192.168.1.2', user_agent='Mozilla/5.0'
        ),
        UserFeedback(
            id='3', feedback_type='feedback', creation_time='2024-08-01T14:34:56Z', username='user3',
            email='user3@example.com', full_name='User Three', content='Great job!',
            user_ip='192.168.1.3', user_agent='Mozilla/5.0'
        ),
        # Add more entries as needed
    ]

    insert_bulk_entries(database, bulk_feedback)
    print("Database populated with test entries successfully.")
