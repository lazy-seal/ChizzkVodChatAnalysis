from Crawler import update_user_info, logger, load_video_info, load_chat_data, save_vod_chats_to_csv, save_video_info_to_csv
from DatabaseManagement import dbObject
from InfoDataObjects import VideoInfo, ChatInfo, UserInfo

import csv
import time
import asyncio
import httpx
from pprint import pprint

async def save_all_chats_from_vod(client: httpx.AsyncClient, video_info: VideoInfo, api_request_limit: int = 5000):
    next_message_time           = 0
    video_number                = video_info.video_number
    streamer_name               = video_info.video_streamer_name
    
    for i in range(api_request_limit):
        chats = await load_chat_data(client, video_number, next_message_time)
        
        if not chats:       # consider changing this to a while loop condition? But that means I have to start with chat being some sort of true value before the loop, I don't like that.
            break
        
        save_vod_chats_to_csv(streamer_name, video_number, chats)
        last_message_time = chats[-1].chat_message_time
        next_message_time = last_message_time + 1
        

async def main():
    streamers   : list[dict[str, str | int]]    = []
    all_videos  : list[list[VideoInfo]]         = []
    video_tasks = []
    chat_tasks  = []
    seen_videos = set()
    
    async with httpx.AsyncClient() as client:
        with open(f"Raw Data\\streamers.csv", "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            async with asyncio.TaskGroup() as tg:
                for row in csv_reader:
                    s_name          = row['streamer_channel_name']
                    s_follower_cout = int(row['streamer_follower_count'])
                    s_channel_id    = row['streamer_channel_id']
                    s_channel_image = row['streamer_channel_image_url']
                    streamers.append(row)
                    task = tg.create_task(load_video_info(client, s_name, s_channel_id, 2))   # @TODO make it accept cient
                    video_tasks.append(task)
        all_videos = [task.result() for task in video_tasks]
        
        with open(f"Raw Data\\videos.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen_videos.add(int(row['video_number']))
        
        async with asyncio.TaskGroup() as tg:
            for streamer_videos in all_videos:
                for video_info in streamer_videos:
                    if video_info.video_number in seen_videos:
                        continue
                    save_video_info_to_csv(video_info)
                    
                    # logger.info("%s's vod: %d", s_name, video_number)
                    task = tg.create_task(save_all_chats_from_vod(client, video_info, 10))
                    chat_tasks.append(task)
                
                    # total_n_messages += n_messages
    
if __name__ == "__main__":
    # up to date as of 2025-12-04
    # streamer_lists_update()
    st = time.time()
    asyncio.run(main())
    print(time.time() - st)

    """ Logic Planning:
    3. For all streamers,
        3-1. Get 50 recent VOD.
    4. For all 50 VOD,
        4-1. input VOD info
        4-2. get all chat into csv
    5. for all chat
        5-1. check if user exists
            5-1-1. if so, get their id to put in as a chat's user
            5-1-2. if not, create new user with WITH AS keyword
        5-2. input chat info
    """