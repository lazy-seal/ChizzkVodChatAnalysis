from DatabaseManagement import localChzzkDbConnection
from pathlib import Path
from InfoDataObjects import VideoInfo, UserInfo, ChatInfo
import csv
import ast
import json 


def main():
    # main database logic brainstorm
    # get videos, input streamer, use their channel id to do make videos
    # ok so I need asynchronous database access to do this fast

    # getting video data
    videos: list[VideoInfo] = []
    with open("TEST\\test_videos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['video_tags'] = ast.literal_eval(row['video_tags'])
            videos.append(VideoInfo(**row)) # type: ignore # Since Video Info is exactly same as the csv I have 
        
    with localChzzkDbConnection(True) as chzzk_db:
        # (WARNING) below sql will drop all table: WARNING
        chzzk_db.execute_sql_script(Path("sql scripts\\table_init.sql"))
        
        # This for loop should be something I call, and should be concurrent
        for video in videos:
            streamer = UserInfo(video.video_streamer_name, video.video_streamer_channel_id)
            # input streamer info, and video info
            chzzk_db.insert_info(streamer)
            chzzk_db.insert_info(video)     # this can be called as soon as I get the VideoInfo object
            
            with open(f"TEST\\{video.video_streamer_name}_{video.video_number}_chats.csv", 'r', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # create chat user and put it into db
                    # create chatinfo and put it into db
                    # the order should be followed to follow foreign key constraint
                    # if chat is anonymous, don't put it?
                    chat_user = UserInfo(row['chat_user_nickname'], row['chat_user_channel_id'])
                    chzzk_db.insert_info(chat_user)
                    
                    if row['chat_donation_amount'] == "":
                        row["chat_donation_amount"] = 0
                    row['chat_extras'] = json.dumps(row['chat_extras'].strip('\"'))
                    chat_info = ChatInfo(**row, chat_video_id=video.video_number) # type: ignore
                    
                    chzzk_db.insert_info(chat_info)



if __name__ == "__main__":
    main()
    
    
            
        
        