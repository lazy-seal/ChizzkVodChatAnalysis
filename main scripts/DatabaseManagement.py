import psycopg2
# import asyncpg
import datetime
import json
from pathlib import Path
from Helpers import print_func_when_called
from InfoDataObjects import UserInfo, ChatInfo, VideoInfo

# make it Singleton?
class localChzzkDbConnection:
    """Context Manager for Database Connection"""
    def __init__(self, is_testing=False):
        with open("Private\\private.json", "r", encoding="utf-8") as f:
            f_json = json.load(f)
            dbpassword = f_json['dbpassword']
        self.conn = psycopg2.connect(host="localhost", 
                                     database="ChzzkChats" if not is_testing else "ChzzkTesting", 
                                     user="postgres", 
                                     password=dbpassword, 
                                     port=5432)
        self.cur = self.conn.cursor()
        self.is_testing = is_testing
    
    def __repr__(self):
        return "localChzzkDbConnection()"
   
    def __enter__(self):
        return self
    
    @print_func_when_called(True)
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Commits (iff not testing) and closes connection and cursor"""
        # if not self.is_testing:
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        
        if exc_type != None:
            print(f"Error Occured: {exc_type}, {exc_value}, {exc_traceback}")
    
    @print_func_when_called()
    def exists_in_db(self, info: ChatInfo | UserInfo | VideoInfo) -> bool:
        """Checks db to see if info (user, chat, vid) exists in db"""
        match info:
            case ChatInfo():
                return False
            case UserInfo():
                self.cur.execute("SELECT * FROM users WHERE user_id = %s", (info.user_channel_id,))
            case VideoInfo():
                self.cur.execute("SELECT * FROM videos WHERE video_id = %s", (info.video_number,))
        return len(self.cur.fetchall()) != 0
    
    @print_func_when_called()
    def insert_info(self, info: ChatInfo | UserInfo | VideoInfo):
        """
        Inserts the info to db
        
        This method checks if the info already exists in db,
        so you don't have to call exists_in_db explicitly somehwere else.
        """
        if self.exists_in_db(info):
            print(f"The info already exists: {info}")
            return
        
        match info:
            case ChatInfo():
                self.cur.execute("INSERT INTO chats VALUES \
                        (%(chat_user_nickname)s, \
                        %(chat_user_channel_id)s, \
                        %(chat_message_time)s, \
                        %(chat_content)s, \
                        %(chat_message_type_code)s, \
                        %(chat_donation_amount)s, \
                        %(chat_extras)s)",
                    info.get_dict()
                    )
            case UserInfo():
                self.cur.execute("INSERT INTO users VALUES (%(user_id)s, %(user_nickname)s)", 
                    (info.user_channel_id, info.user_nickname))
            case VideoInfo():
                self.cur.execute("INSERT INTO videos VALUES \
                        (%(video_streamer_name)s, \
                        %(video_streamer_channel_id)s, \
                        %(video_number)s, \
                        %(video_title)s, \
                        %(video_duration)s, \
                        %(video_tags)s, \
                        %(video_category_type)s, \
                        %(video_category)s, \
                        %(video_publish_date)s)", 
                    info.get_dict()
                    )
          
    @print_func_when_called()
    def insert_statistics_for_vod(self, video_number: int):
        """
        	Performs query to find: 
                video_chat_count, 
                video_total_donation_amount, 
                video_active_user_count INTEGER
            And inserts them into corresponding video row
        """
        raise NotImplementedError
    
    @print_func_when_called()
    def execute_sql_script(self, file_path: Path):
        """executes sql script"""
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
            self.cur.execute(script)
            
    # @print_func_when_called(True)
    # def execute_sql_statement(self, statement: str):
    #     """executes sql statement"""
    #     self.cur.execute(statement)   # obvious protection against sql injection needed

if __name__ == "__main__":
    # with localChzzkDbConnection() as chzzk_db:
    #     chzzk_db.execute_sql_script(Path("sql scripts\\table_init.sql"))
    """
    First, check if the streamer already exists on the users
    if not, put in the user.
    
    Use the streamer's id to create video_streamer_id
    """
    # @TODO study async postgreSQL methodology
    # @TODO chat
    # @TODO function to store a bunch of chat int db
    
