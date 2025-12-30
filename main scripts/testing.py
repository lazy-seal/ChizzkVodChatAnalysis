from DatabaseManagement import localChzzkDbConnection
from pathlib import Path
from InfoDataObjects import VideoInfo, UserInfo, ChatInfo
import csv
import ast
import json 

from Crawler import logger

def main():
    # main database logic brainstorm
    # get videos, input streamer, use their channel id to do make videos
    # ok so I need asynchronous database access to do this fast

    # getting video data
    videos: list[VideoInfo] = []
    with open("Raw Data\\videos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['video_tags'] = ast.literal_eval(row['video_tags'])
            videos.append(VideoInfo(**row)) # type: ignore # Since Video Info is exactly same as the csv I have 
        
    with localChzzkDbConnection(is_testing=True) as chzzk_db:
        # (WARNING) below sql will drop all table: WARNING
        chzzk_db.execute_sql_script(Path("sql scripts\\table_init.sql"))

        # This for loop should be something I call, and should be concurrent
        for video in videos:
            streamer = UserInfo(video.video_streamer_name, video.video_streamer_channel_id)
            # input streamer info, and video info
            
            chzzk_db.insert_info(streamer)
            chzzk_db.insert_info(video)     # this can be called as soon as I get the VideoInfo object
            
            # turn this into a function?
            with open(f"Raw Data\\Chats\\{video.video_streamer_name}_{video.video_number}_chats.csv", 'r', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                logger.info(f"Started inserting chat for {video}")
                print(f"Started inserting chat for {video}")
                for row in reader:
                    try:
                        # create chat user and put it into db
                        # create chatinfo and put it into db
                        # the order should be followed to follow foreign key constraint
                        # if chat is anonymous, don't put it?
                        chat_user = UserInfo(row['chat_user_nickname'], row['chat_user_channel_id'])
                        chzzk_db.insert_info(chat_user)
                        if not row['chat_donation_amount']:
                            row["chat_donation_amount"] = 0
                        row['chat_extras'] = json.dumps(row['chat_extras'].strip('\"'))
                        chat_info = ChatInfo(**row, chat_video_id=video.video_number) # type: ignore
                        
                        chzzk_db.insert_info(chat_info)
                    except Exception as e:
                        print(f"Error occurred: {e}")
                        print(f"Was processing chat: {row}")
           
            # now that chat is inserted, I can add the video statistics 
            chzzk_db.insert_statistics_for_vod(int(video.video_number))



if __name__ == "__main__":
    main()
    
    
            
        
        