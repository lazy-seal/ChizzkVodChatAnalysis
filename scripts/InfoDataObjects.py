from dataclasses import dataclass
from typing import NamedTuple
from pprint import pprint
import ast

# @TODO make abstract base class for infodataobject

class CHZZK_URL:
    def __init__(self):
        pass
    """
    videos: f"https://api.chzzk.naver.com/service/v1/channels/{streamer_channel_id}/videos"
    users: f"https://api.chzzk.naver.com/service/v1/channels/{user_channel_id}"
    chat: f"https://api.chzzk.naver.com/service/v1/videos/{video_number}/chats?playerMessageTime={message_time}"
    """

# @TODO file path with enum?
"""
Path("Raw Data\\streamers.csv")
Path("Raw Data\\users.csv")
Path("Raw Data\\videos.csv")
Path(f"Raw Data\\Chats\\{streamer_name}_{video_number}_chats.csv")
"""



STREAMERS_CSV_HEADER = [
    "streamer_nickname",
    "streamer_channel_id",
]

class StreamerInfo(NamedTuple):
    streamer_nickname: str
    streamer_channel_id: str

@dataclass
class VideoInfo():  
    video_streamer_name: str
    video_streamer_channel_id: str
    video_number: int
    video_title: str
    video_duration: int
    video_tags: list[str] 
    video_category_type: str
    video_category: str
    video_publish_date: str
    video_chat_count: int = -1
    video_total_donation_amount: int = -1
    video_active_user_count: int = -1
    
    
    VIDEOS_CSV_HEADER = [
        "video_streamer_name",
        "video_streamer_channel_id",
        "video_number",
        "video_title",
        "video_duration",
        "video_tags",
        "video_category_type",
        "video_category",
        "video_publish_date",
        "video_chat_count",
        "video_total_donation_amount",
        "video_active_user_count"
    ]
    
    def to_store_in_csv(self):
        return {
            "video_streamer_name"   : self.video_streamer_name,
            "video_streamer_channel_id" : self.video_streamer_channel_id,
            "video_number"              : self.video_number,
            "video_title"               : self.video_title,
            "video_duration"            : self.video_duration,
            "video_tags"                : self.video_tags,
            "video_category_type"       : self.video_category_type,
            "video_category"            : self.video_category,
            "video_publish_date"        : self.video_publish_date,
            "video_chat_count"          : self.video_chat_count,
            "video_total_donation_amount" : self.video_total_donation_amount,
            "video_active_user_count"   : self.video_active_user_count,
        }
    
    def to_store_in_db(self):
        return int(self.video_number), \
            str(self.video_streamer_channel_id), \
            str(self.video_title), \
            int(self.video_duration), \
            self.video_tags, \
            str(self.video_category_type), \
            str(self.video_category), \
            str(self.video_publish_date)
    
@dataclass
class ChatInfo():
    chat_user_nickname: str
    chat_user_channel_id: str
    chat_message_time: int
    chat_content: str
    chat_emojis: dict
    chat_user_device_os: str
    chat_message_type_code: str
    chat_donation_amount: int = 0
    chat_video_id: int = 0

    CHATS_CSV_HEADER = [
        "chat_user_nickname",
        "chat_user_channel_id",
        "chat_message_time",
        "chat_content",
        "chat_message_type_code",
        "chat_donation_amount",
        "chat_emojis",
    ]
    
    def get_dict(self):
        return {
            "chat_user_channel_id"      : self.chat_user_channel_id,
            "chat_video_id"             : self.chat_video_id,
            "chat_user_nickname"        : self.chat_user_nickname,
            "chat_message_time"         : self.chat_message_time,
            "chat_content"              : self.chat_content,
            "chat_message_type_code"    : self.chat_message_type_code,
            "chat_donation_amount"      : self.chat_donation_amount,
            "chat_emojis"               : self.chat_emojis,
        }
    
    def to_store_in_db(self):
        return str(self.chat_user_channel_id), \
            int(self.chat_video_id), \
            int(self.chat_message_time), \
            self.chat_content, \
            self.chat_message_type_code, \
            int(self.chat_donation_amount), \
            self.chat_user_device_os, \
            str(self.chat_emojis).replace('\'', '\"'), \
            # str(self.chat_emojis) if self.chat_emojis else "",

            

@dataclass
class UserInfo():
    user_nickname: str
    user_channel_id: str
    user_channel_description: str | None = None
    user_follower_count: int | None = None
    user_channel_type: str | None = None  # "STREAMING" or "NORMAL", plus maybe something else I haven't seen
    
    def get_dict(self):
        return {
            "user_nickname": self.user_nickname,
            "user_channel_id": self.user_channel_id,
            "user_channel_description": self.user_channel_description,
            "user_follower_count": self.user_follower_count,
            "user_channel_type": self.user_channel_type
        }
    
    def __hash__(self):
        return hash(self.user_channel_id)
    
    def __eq__(self, other):
        return self.user_channel_id == other.user_channel_id
    
    def __lt__(self, other):
        return self.user_channel_id < other.user_channel_id
        
        
if __name__ == "__main__":
    pprint(VideoInfo.__dict__)