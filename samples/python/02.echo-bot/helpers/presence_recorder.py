import duckdb
import datetime
import os

class PresenceRecorder:
    def __init__(self):
        """
        Initialize database connection, create table for user activity and load data from csv if available. 
        """
        self.conn = duckdb.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute("""DROP TABLE IF EXISTS user_activity""")
        self.c.execute("""
            CREATE TABLE user_activity (
            member_id VARCHAR PRIMARY KEY,
            last_active VARCHAR
            )
        """)
        if os.path.exists('user_activity.csv'):
            self.conn.execute("COPY user_activity FROM 'user_activity.csv' (HEADER)")

    def store_activity(self, member_id) -> None:
        """
        Stores the user's activity by the date.

        Args:
        member_id : str
            ID of the member.
        
        Output: None
        """

        date_str = datetime.datetime.now().strftime("%d-%m-%Y")

        self.c.execute(
            f"INSERT INTO user_activity (member_id, last_active) VALUES ('{member_id}', '{date_str}') "
            f"ON CONFLICT (member_id) DO UPDATE SET last_active = '{date_str}'"
        )
        
        self.conn.commit()
        self.conn.execute("COPY user_activity TO 'user_activity.csv' (HEADER)")

    def retrieve_activity(self, member_id) -> str:
        """
        Retrieves the last active date of the user.

        Args:
        member_id : str
            ID of the member.

        Returns: 
        str : last active date of the user
        """

        self.c.execute(f"SELECT last_active FROM user_activity WHERE member_id = '{member_id}'")
        row = self.c.fetchone()
        return row[0] if row else None