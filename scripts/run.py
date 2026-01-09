from Crawler import logger, load_video_info, load_chat_and_user_data, write_vod_chats_to_csv, write_video_info_to_csv
from DatabaseManagement import localChzzkDbConnection
from InfoDataObjects import VideoInfo, ChatInfo, UserInfo
from pathlib import Path

import csv
import time
import asyncio
import httpx
from pprint import pprint
from tenacity import retry, stop_after_attempt, wait_exponential 

@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier=1, min=5, max=120)
)
async def fetch_and_save_chats_to_db(db:localChzzkDbConnection, client: httpx.AsyncClient, 
                                     video_number: int, api_request_limit: int = 5000): 
    """Saves all chats of the given video to database"""
    async def insert_user_and_chats_to_db(users, chats):
        await db.insert_info(sorted(users))     # sort names to prevent deadlock condition
        await db.insert_info(chats)     

    next_message_time   = 0 
    starttime           = time.time()
    
    logger.info("Fetch Started on vod: %d", video_number)

    async with asyncio.TaskGroup() as tg: 
        for _ in range(api_request_limit):
            chats, users = await load_chat_and_user_data(client, video_number, next_message_time)
            
            if not chats:      
                elapsed = time.time() - starttime
                logger.info(f"{video_number} download took {int(elapsed) // 60}m {int(elapsed % 60)}s")
                break
            
            tg.create_task(insert_user_and_chats_to_db(users, chats))

            last_message_time = chats[-1].chat_message_time
            next_message_time = last_message_time + 1

    elapsed = time.time() - starttime
    logger.info(f"{video_number} db write took {int(elapsed) // 60}m {int(elapsed % 60)}s")


async def get_video_lists(client: httpx.AsyncClient, path: Path, n_videos_to_get: int = 50):
    """given path to the files to the streamers, return lists of VideoInfo"""
    video_tasks = []
    with open(path, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        async with asyncio.TaskGroup() as tg:
            for row in csv_reader:
                s_channel_id    = row['channel_id']
                task = tg.create_task(load_video_info(client, s_channel_id, n_videos_to_get))
                video_tasks.append(task)
                break
    return [task.result() for task in video_tasks]

async def main():
    all_videos_per_streamer : list[list[VideoInfo]] = []    # list of streamers' list of videos: Each sublist is list of VideoInfo from the same streamer 
    is_testing = False
    num_videos_per_streamer = 50
    streamers_csv = Path("Raw Data\\all_verified_streamers.csv")
     
    async with localChzzkDbConnection(is_testing) as chzzkdb:
        async with httpx.AsyncClient() as client:
            all_videos_per_streamer = await get_video_lists(client, streamers_csv, num_videos_per_streamer) 

            if chzzkdb.is_testing:  # resets database if I'm testing
                await chzzkdb.execute_sql_script(Path("sql scripts\\table_init.sql"))

            async with asyncio.TaskGroup() as tg:
                for streamer_videos in all_videos_per_streamer:
                    if streamer_videos:
                        s_name = streamer_videos[0].video_streamer_name
                        s_id = streamer_videos[0].video_streamer_channel_id
                        streamer = UserInfo(s_name, s_id) 
                        await chzzkdb.insert_info([streamer])           # insert streamer first to ensure foreing key constraint
                        await chzzkdb.insert_info(streamer_videos)      # Same here. Chats require videos to exist in the first place

                    for video_info in streamer_videos:
                        if await chzzkdb.insert_info([video_info]):
                            video_number = video_info.video_number
                            tg.create_task(fetch_and_save_chats_to_db(chzzkdb, client, video_number))
            
        # Create new taskgroup to make sure all relevant data for video are inserted
        async with asyncio.TaskGroup() as tg:
            for streamer_videos in all_videos_per_streamer:
                for video_info in streamer_videos:
                    tg.create_task(chzzkdb.insert_statistics_for_vod(video_info.video_number))
    
if __name__ == "__main__":
    st = time.time()
    asyncio.run(main())
    elapsed = time.time() - st
    print(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
    logger.info(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
