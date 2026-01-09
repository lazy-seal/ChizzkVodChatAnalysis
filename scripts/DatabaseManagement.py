import psycopg2
from pprint import pprint
import asyncpg
import datetime
import json
from pathlib import Path
from Helpers import print_func_when_called
from InfoDataObjects import UserInfo, ChatInfo, VideoInfo
from Crawler import logger
from collections.abc import Iterable
import asyncio


class localChzzkDbConnection:
    """Context Manager for Database Connection"""
    def __init__(self, is_testing=False):
        self.pool : asyncpg.Pool = None # type: ignore
        self.is_testing = is_testing
    
    def __repr__(self):
        return "localChzzkDbConnection()"
   
    @print_func_when_called()
    async def __aenter__(self):
        with open("Private\\private.json", "r", encoding="utf-8") as f:
            f_json = json.load(f)
            dbpassword = str(f_json['dbpassword'])
        self.pool = await asyncpg.create_pool(host="localhost", 
                                     database="ChzzkChats" if not self.is_testing else "ChzzkTesting", 
                                     user="postgres", 
                                     password=dbpassword, 
                                     port=5432,
                                     ssl=False,
                                     min_size=10,
                                     max_size=100)

        return self
    
    @print_func_when_called()
    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        """Commits (iff not testing) and closes connection and cursor"""
        # if not self.is_testing:
        if  self.pool:
            print('start closing connections')
            await asyncio.wait_for(self.pool.close(), timeout=5.0)
            print('pool closed')
             
        if exc_type != None:
            print(f"Error Occured: {exc_type}, {exc_value}")
    
    # @print_func_when_called()
    async def exists_in_db(self, info: ChatInfo | UserInfo | VideoInfo) -> bool: # type: ignore
        """Checks db to see if info (user, chat, vid) exists in db"""
        async with self.pool.acquire() as con:
            lookup_result = [] 
            match info:
                case ChatInfo():
                    # I don't think this would be used.  
                    # But I still should implement this
                    # @TODO
                    return False    # what determines if two chats are the same?
                case UserInfo():
                    lookup_result = await con.fetch("SELECT * FROM users WHERE user_id = $1", info.user_channel_id)
                case VideoInfo():
                    lookup_result = await con.fetch("SELECT * FROM videos WHERE video_id = $1", int(info.video_number))
        
        return len(lookup_result) != 0
    
    
    # @print_func_when_called()
    async def insert_info(self, info_list: Iterable[ChatInfo] | Iterable[UserInfo] | Iterable[VideoInfo]) -> bool:
        """
        Inserts the info to db. Returns True if insert was successful, False otherwise.
        
        This method **does not check if the info already exists in db**,
        but accomadates it by creating a temperary table and left-joining it to the
        actual db
        """
        match info_list:
            case [ChatInfo(), *_]:
                try:
                    i = 0
                    info = None
                    for info in info_list:
                        i += 1
                        json.loads(info.to_store_in_db()[-1])
                except Exception as e:
                   logger.warning("Error while json conversion: ") 
                   logger.warning(str(info))
                   del info_list[i] # type: ignore
                records = [info.to_store_in_db() for info in info_list]
                query = """
                    INSERT INTO chats (
                        chat_user_id, chat_video_id, chat_message_time,
                        chat_content, chat_message_type_code,
                        chat_donation_amount, chat_user_device_os,
                        chat_emojis 
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                """
                await self.pool.executemany(query, records)
            case [UserInfo(), *_]:
                records = [(info.user_channel_id, info.user_nickname) for info in info_list]
                query = """
                    INSERT INTO users (user_id, user_nickname)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO NOTHING
                """
                await self.pool.executemany(query, records)
            case [VideoInfo(), *_]:
                records = [info.to_store_in_db() for info in info_list]
                query = """
                    INSERT INTO videos (
                        video_id,
                        video_streamer_id,
                        video_title,
                        video_duration,
                        video_tags,
                        video_category_type,
                        video_category,
                        video_publish_date
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (video_id) DO NOTHING
                """
                await self.pool.executemany(query, records)
            case _:
                raise TypeError(f"wrong input format: {type(info_list)} for {info_list}")

        return True
        # logger.info(f"successfully inserted: {info}")
              
    # @print_func_when_called(True)
    async def insert_statistics_for_vod(self, video_number: int):
        """
            Performs query to find: 
                video_chat_count, 
                video_total_donation_amount, 
                video_active_user_count INTEGER
            And inserts them into corresponding video row
        """
        if type(video_number) != int:
            raise TypeError("The video_number has to be an integer")

        async with self.pool.acquire() as con:
            # video_chat_count, video_total_donation_amount, video_active_user_count
            # maybe I can make the below statement into a single one
            result = await con.fetch("""SELECT 
                                COUNT(*) AS video_chat_count, 
                                COALESCE(SUM(chat_donation_amount)) AS video_total_donation_amount, 
                                COUNT(DISTINCT chat_user_id) AS video_active_user_count
                             FROM chats WHERE chat_video_id = $1""", video_number)
            video_chat_count, video_total_donation_amount, video_active_user_count = result[0][0], result[0][1], result[0][2] 
            await con.execute("""UPDATE videos
                                SET video_chat_count = $1,
                                    video_total_donation_amount = $2,
                                    video_active_user_count = $3 
                                WHERE video_id = $4 
                             """, video_chat_count, video_total_donation_amount, video_active_user_count, video_number
                            )

    # this function should be gone
    # replace it by: initialize db or something
    @print_func_when_called()
    async def execute_sql_script(self, file_path: Path):
        """executes sql script"""
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
            async with self.pool.acquire() as con:
                await con.execute(script)
            
    # I abstracted out the sql statement from the crawler and db manage
    # db manager will execute pre-written queries only and provide functionality
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
    pass