from types import coroutine
from DatabaseManagement import localChzzkDbConnection
from pathlib import Path
from InfoDataObjects import VideoInfo, UserInfo, ChatInfo
import csv
import ast
import json 
import asyncio
from pprint import pprint
import httpx
import time

from Crawler import logger
"""
Raw Data\\videos.csv
Raw Data\\Chats\\{video.video_streamer_name}_{video.video_number}_chats.csv
"""

async def fetch_and_save_chats_to_db(chzzk_db:localChzzkDbConnection, video: VideoInfo): 
    with open(f"Raw Data\\Chats\\{video.video_streamer_name}_{video.video_number}_chats.csv", 'r', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        start = time.time()
        # logger.info(f"Started inserting chat for {video.video_streamer_name}'s videor: {video.video_number}")
        # print(f"Started inserting chat for {video.video_streamer_name}'s video: {video.video_number}")
        users : set[UserInfo] = set()
        chats : list[ChatInfo] = []
        for row in reader:
            try:
                # create chat user and put it into db
                # create chatinfo and put it into db
                # the order should be followed to follow foreign key constraint
                # if chat is anonymous, don't put it?
                chat_user = UserInfo(row['chat_user_nickname'], row['chat_user_channel_id'])
                users.add(chat_user)
                if not row['chat_donation_amount']:
                    row["chat_donation_amount"] = 0
                row['chat_content'] = row['chat_content'].replace('\x00', "")
                row['chat_extras'] = json.dumps(row['chat_extras'].strip('\"'))
                chat_info = ChatInfo(**row, chat_video_id=video.video_number) # type: ignore
                
                # print([chat_info])
                # await chzzk_db.insert_info([chat_user])
                # await chzzk_db.insert_info([chat_info])
                
                chats.append(chat_info)
            except Exception as e:
                logger.warning(f"Error occurred: {e}")
                logger.warning(f"Was processing chat: {row}")
                break
        # logger.info(f'{len(users)} user inserting started')
        sorted_users = sorted((*users,))
        await chzzk_db.insert_info(sorted_users)
        logger.info(f'{len(chats)} chats inserting started')
        await chzzk_db.insert_info(chats)
        elapsed = time.time() - start
        print(f"{video.video_number} finished at: {elapsed:.2f}")
        logger.info(f"{video.video_number} finished at: {elapsed:.2f}")

async def main():
    # getting video data
    videos: list[VideoInfo] = []
    with open("Raw Data\\videos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['video_tags'] = ast.literal_eval(row['video_tags'])
            videos.append(VideoInfo(**row)) # type: ignore # Since Video Info is exactly same as the csv I have 
        
    async with localChzzkDbConnection(is_testing=True) as chzzk_db:
        async with asyncio.TaskGroup() as tg:
            # (WARNING) below sql will drop all table: WARNING
            await chzzk_db.execute_sql_script(Path("sql scripts\\table_init.sql"))
            # This for loop should be something I call, and should be concurrent
            for video in videos:
                streamer = UserInfo(video.video_streamer_name, video.video_streamer_channel_id)
                # if video.video_number != "10407680":
                    # continue

                # input streamer info, and video info
                await chzzk_db.insert_info([streamer])
                await chzzk_db.insert_info([video])     # this can be called as soon as I get the VideoInfo object
                
                tg.create_task(fetch_and_save_chats_to_db(chzzk_db, video))

                # now that chat is inserted, I can add the video statistics 
                await chzzk_db.insert_statistics_for_vod(int(video.video_number))


if __name__ == "__main__":
    asyncio.run(main())
    
    
            
        
        