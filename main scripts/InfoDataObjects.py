from dataclasses import dataclass
from typing import NamedTuple
from pprint import pprint

VIDEOS_CSV_HEADER = [
    "video_streamer_name",
    "video_streamer_channel_id",
    "video_number",
    "video_title",
    "video_duration",
    "video_tags",
    "video_category_type",
    "video_category",
    "video_publish_date"
]


CHATS_CSV_HEADER = [
    "chat_user_nickname",
    "chat_user_channel_id",
    "chat_message_time",
    "chat_content",
    "chat_message_type_code",
    "chat_donation_amount",
    "chat_extras"
]

USERS_CSV_HEADER = [
    # @TODO fill in
]

STREAMERS_CSV_HEADER = [
    "streamer_channel_name",
    "streamer_channel_id",
    "streamer_follower_count",
    "streamer_channel_image_url"
]

class VideoInfo(NamedTuple):
    video_streamer_name: str
    video_streamer_channel_id: str
    video_number: int
    video_title: str
    video_duration: int
    video_tags: str     # this is in "['a1', 'b3', 'c2']" format
    video_category_type: str
    video_category: str
    video_publish_date: str
    # video_chat_count: int
    # video_total_donation_amount: int
    # video_active_user_count: int
    
    def get_dict(self):
        return {
            "video_streamer_name"   : self.video_streamer_name,
            "video_streamer_channel_id" : self.video_streamer_channel_id,
            "video_number"              : self.video_number,
            "video_title"               : self.video_title,
            "video_duration"            : self.video_duration,
            "video_tags"                : self.video_tags, 
            "video_category_type"       : self.video_category_type,
            "video_category"            : self.video_category,
            "video_publish_date"        : self.video_publish_date
        }
    
class ChatInfo(NamedTuple):
    chat_user_nickname: str
    chat_user_channel_id: str
    chat_message_time: int
    chat_content: int
    chat_message_type_code: int
    chat_donation_amount: int
    chat_extras: str
    
    def get_dict(self):
        return {
            "chat_user_nickname"        : self.chat_user_nickname,
            "chat_user_channel_id"      : self.chat_user_channel_id,
            "chat_message_time"         : self.chat_message_time,
            "chat_content"              : self.chat_content,
            "chat_message_type_code"    : self.chat_message_type_code,
            "chat_donation_amount"      : self.chat_donation_amount,
            "chat_extras"               : self.chat_extras
        }

class UserInfo(NamedTuple):
    user_channel_id: str
    user_nickname: str
    user_follower_count: int
    user_different_names: list[str]
    user_channel_type: str  # "STREAMING" or "NORMAL", plus maybe something else I haven't seen
    
    def get_dict(self):
        return {
            "user_channel_id": self.user_channel_id,
            "user_nickname": self.user_nickname,
            "user_follower_count": self.user_follower_count,
            "user_different_names": self.user_different_names,
            "user_channel_type": self.user_channel_type
        }
    
    
if __name__ == "__main__":
    pprint(VideoInfo.__dict__)