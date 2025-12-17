import psycopg2
import json
from pathlib import Path

# make it Singleton?
class dbObject:
    def __init__(self):
        with open("private.json", "r", encoding="utf-8") as f: #@TODO make resource.json or other file to store private data
            f_json = json.load(f)
            dbpassword = f_json['dbpassword']
        self.conn = psycopg2.connect(host="localhost", dbname="ChzzkChats", user="postgres", password=dbpassword, port=5432)
        self.cur = self.conn.cursor()
    
    def exists_in_db(self, info) -> bool:
        """Checks db to see if info (user, chat, vid) exists in db"""
        raise NotImplementedError

    def get_cursor(self):
        return self.cur
    
    def end_session(self):
        if not self.cur:
            print("No session to close")
        self.cur.close()
        self.conn.close()
    
    def execute_sql_script(self, file_path: Path):
        """executes sql script"""
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
            self.cur.execute(script)
    
    def insert_info(self, info) -> bool:
        """Inserts the info to db"""
        raise NotImplementedError
    
    def execute_sql_statement(self, statement: str):
        """executes sql statement"""
        raise NotImplementedError

if __name__ == "__main__":
    chatdb = dbObject()
    # chatdb.connectToChzzkChats()
    chatdb.get_cursor()
    
    # code here to implement
    """
    First, check if the streamer already exists on the users
    if not, put in the user.
    
    Use the streamer's id to create video_streamer_id
    """
    
    chatdb.end_session()
    
    # @TODO study async postgreSQL methodology
    # @TODO chat
        # @TODO function to store a bunch of chat int db
    
