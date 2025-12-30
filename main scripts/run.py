from Crawler import logger, load_video_info, load_chat_data, save_vod_chats_to_csv, save_video_info_to_csv
from DatabaseManagement import localChzzkDbConnection
from InfoDataObjects import VideoInfo, ChatInfo, UserInfo
from pathlib import Path

import csv
import time
import asyncio
import httpx
from pprint import pprint

async def fetch_and_save_chats_to_csv(client: httpx.AsyncClient, video_info: VideoInfo, api_request_limit: int = 5000):
    next_message_time           = 0
    video_number                = video_info.video_number
    streamer_name               = video_info.video_streamer_name
    
    for _ in range(api_request_limit):
        chats = await load_chat_data(client, video_number, next_message_time)
        
        if not chats:       # consider changing this to a while loop condition? But that means I have to start with chat being some sort of true value before the loop, I don't like that.
            break
        
        save_vod_chats_to_csv(streamer_name, video_number, chats)
        last_message_time = chats[-1].chat_message_time
        next_message_time = last_message_time + 1

async def fetch_and_save_chats_to_db(db:localChzzkDbConnection, client: httpx.AsyncClient, video_info: VideoInfo, api_request_limit: int = 5000): 
    next_message_time           = 0
    video_number                = video_info.video_number
    
    for _ in range(api_request_limit):
        chats = await load_chat_data(client, video_number, next_message_time)
        
        if not chats:       # consider changing this to a while loop condition? But that means I have to start with chat being some sort of true value before the loop, I don't like that.
            break
        
        for chat in chats:
            db.insert_info(chat)     # I want to turn this coroutine object

        last_message_time = chats[-1].chat_message_time
        next_message_time = last_message_time + 1


async def get_video_lists(client: httpx.AsyncClient, path: Path):
    """given path to the files to the streamers, return lists of VideoInfo"""
    video_tasks = []
    with open(f"Raw Data\\streamers.csv", "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        async with asyncio.TaskGroup() as tg:
            for row in csv_reader:
                s_channel_id    = row[0]
                task = tg.create_task(load_video_info(client, s_channel_id, 2))
                video_tasks.append(task)
    return [task.result() for task in video_tasks]

async def main():
    all_videos : list[list[VideoInfo]] = []
    
    async with httpx.AsyncClient() as client:
        all_videos = await get_video_lists(client, Path()) 
        
        async with asyncio.TaskGroup() as tg:
            with localChzzkDbConnection(is_testing=True) as chzzkdb:
                for streamer_videos in all_videos:
                    if streamer_videos:
                        streamer = UserInfo(streamer_videos[0].video_streamer_name, streamer_videos[0].video_streamer_channel_id)
                        chzzkdb.insert_info(streamer)
                    for video_info in streamer_videos:
                        if chzzkdb.insert_info(video_info):
                            # logger.info("%s's vod: %d", s_name, video_number)
                            tg.create_task(fetch_and_save_chats_to_db(chzzkdb, client, video_info, 10))
                    
                        # total_n_messages += n_messages
    
if __name__ == "__main__":
    # up to date as of 2025-12-04
    # streamer_lists_update()
    st = time.time()
    asyncio.run(main())
    print(time.time() - st)
