import psycopg2
# import asyncpg
import datetime
import json
from pathlib import Path
from Helpers import print_func_when_called

# make it Singleton?
class localChzzkDbConnection:
    """Context Manager for Database Connection"""
    @print_func_when_called
    def __init__(self):
        with open("Private\\private.json", "r", encoding="utf-8") as f: #@TODO make resource.json or other file to store private data
            f_json = json.load(f)
            dbpassword = f_json['dbpassword']
        self.conn = psycopg2.connect(host="localhost", database="ChzzkChats", user="postgres", password=dbpassword, port=5432)
        self.cur = self.conn.cursor()
    
    @print_func_when_called
    def __enter__(self):
        return self
    
    @print_func_when_called
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cur.close()
        self.conn.close()
    
    @print_func_when_called
    def exists_in_db(self, info) -> bool:
        """Checks db to see if info (user, chat, vid) exists in db"""
        raise NotImplementedError
    
    @print_func_when_called
    def execute_sql_script(self, file_path: Path):
        """executes sql script"""
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
            self.cur.execute(script)
    
    @print_func_when_called
    def insert_info(self, info) -> bool:
        """Inserts the info to db"""
        raise NotImplementedError
    
    @print_func_when_called
    def execute_sql_statement(self, statement: str):
        """executes sql statement"""
        self.cur.execute(statement)   # obvious protection against sql injection needed

if __name__ == "__main__":
    with localChzzkDbConnection() as chzzk_db:
        chzzk_db.execute_sql_statement("DROP TABLE IF EXISTS chats, videos, users CASCADE;")
        pass
    # chatdb.connectToChzzkChats()
    
    # code here to implement
    """
    First, check if the streamer already exists on the users
    if not, put in the user.
    
    Use the streamer's id to create video_streamer_id
    """
    
    # @TODO study async postgreSQL methodology
    # @TODO chat
    # @TODO function to store a bunch of chat int db
    
