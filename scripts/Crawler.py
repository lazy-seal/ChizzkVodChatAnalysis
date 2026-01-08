import json
import ast
import csv
from pathlib import Path
import logging
from pprint import pprint
import httpx
import asyncio
import pandas as pd
from InfoDataObjects import VideoInfo, ChatInfo, UserInfo, StreamerInfo, VIDEOS_CSV_HEADER, CHATS_CSV_HEADER, STREAMERS_CSV_HEADER


with open("Private//private.json", encoding="utf-8") as f:
        private_file = json.load(f)
        HEADERS = {"User-Agent": "Mozilla/5.0",
                   "Client-ID": private_file['Client-ID']}

logger = logging.getLogger(__name__)
logging.basicConfig(filename='Crawler.log', encoding='utf-8', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def load_user_info(client: httpx.AsyncClient, user_channel_id: str) -> UserInfo | None:
    """
    Sends http request to Chzzk api to get a relevant info of the user
    
    Parameter:
        client (httpx.AsyncClient): client to perform api request
        user_channel_id (str): user-identifying id to send a request
        
    Returns:
        UserInfo | None: returns fetched user_info, or None if the user is no longer available
    
    Raises:
        ConnectionError if the user_request wasn't successful
    """
    url = f"https://api.chzzk.naver.com/service/v1/channels/{user_channel_id}"
    res = await client.get(url=url, headers=HEADERS)
    
    # knwon responses:
    # 200: great
    # 500/9002: "이 채널은 네이버 운영 정책을 위반하여 일시적으로 이용할 수 없습니다."
        # 채널 정지당한 계정
    
    match res.status_code:
        case 500 | 9002:    # "이 채널은 네이버 운영 정책을 위반하여 일시적으로 이용할 수 없습니다."
            return None
        case 200:
            pass
        case _:
            raise ConnectionError(f"Fetching info not successful for user{user_channel_id}: {res}")

    content = res.json()['content']
    
    if content['channelName'] == "(알 수 없음)":    # idk why i put this. I can't remember where I've seen this
        logger.info(content)
        pprint(content)
    
    user_info = UserInfo(
        user_nickname               = content['channelName'],
        user_channel_id             = content['channelId'],
        user_channel_description    = content['channelDescription'].replace("\n", " "),
        user_follower_count         = content['followerCount'],
        user_channel_type           = content['channelType'],       # "NORMAL" or "STREAMING"
    )
    return user_info


async def load_video_info(client: httpx.AsyncClient, streamer_channel_id, n_videos_to_load=50) -> list[VideoInfo]:
    """
    Description:
        Sends http request to Chzzk api to get a relevant info of the video
 
    Parameters:
        n_videos_to_load (int) : number of video information you want to request. \
            Maximum is 50 (enforced with ValueError). The api gives no response if greater than 50.
        
    Returns:
        vods (list[VideoInfo])
    
    Request url:
        "https://api.chzzk.naver.com/service/v1/channels/{streamer_channel_id}/videos"
    """
    if n_videos_to_load > 50:
        raise ValueError("The size needs to be less than 50. Otherwise, you get https error. Might change later on, depending on how Chzzk wants api to be.")
    
    vods        = []
    url         = f"https://api.chzzk.naver.com/service/v1/channels/{streamer_channel_id}/videos"
    params      = {"size": n_videos_to_load}
    res         = await client.get(url, params=params, headers=HEADERS)
    
    if res.status_code != 200:
        raise ConnectionError(f"the api call was not successful:{res}")
    
    res_json = res.json()
    
    # logger.info(res_json)
    # pprint(res_json)
    for video in res_json["content"]["data"]:
        video_info = VideoInfo(
            video_streamer_name         = video['channel']['channelName'],
            video_streamer_channel_id   = streamer_channel_id,
            video_number                = int(video['videoNo']),
            video_title                 = video['videoTitle'].replace("\n", " "),
            video_duration              = int(video['duration']),
            video_tags                  = video['tags'],
            video_category_type         = video['categoryType'],
            video_category              = video['videoCategory'],
            video_publish_date          = video['publishDate']
        )
        vods.append(video_info)
    return vods

async def load_chat_and_user_data(client: httpx.AsyncClient, video_number: int, message_time: int) -> tuple[list[ChatInfo], set[UserInfo]]:
    """
    Description:
        Sends http request to Chzzk api to get a relevant info of the chat within the given video within the given time (~200 chats each)
    
    Parameters:
        client (httpx.AsyncClient): the client to perform http request
        video_number (int): video identification number unique to each replay.
        message_time (int): A timestamp within the video in which the api call will request chats. 
            Ex.: given 0, the function requests chats from the beginning of the video
    
    Returns:
        chats (list[ChatInfo]): is a list of ChatInfo objects
            
    Request URL:
        "https://api.chzzk.naver.com/service/v1/videos/{video_number}/chats?playerMessageTime={next_player_message_time}"
        
    Extra Note:
        Logger will give you warning when unkown messageTypeCode is encountered. 
        Current Known messageTypes are:
            1: regular chat
            10: donation
            11: Subscription
            12: Gifts (구독권 등)
            13: System Message: "PARTY_DONATION_CONFIRM"
            30: System Message: "이모티콘 전용 모드 해제"
    """
    url = f"https://api.chzzk.naver.com/service/v1/videos/{video_number}/chats?playerMessageTime={message_time}"
    response = await client.get(url=url, headers=HEADERS, timeout=500)
    res_json = response.json()
    chats: list[ChatInfo] = []
    users: set[UserInfo] = set()
    
    if response.status_code != 200 or len(res_json['content']['videoChats']) == 0:
        logger.info("Fetch Finished on vid %d: status_code: %d", video_number, response.status_code)
        return [], set() 
    elif response.status_code != 200:
        logger.warning("Fetch not successful on vid %d: %s", video_number, response)
        return [], set()

    for chat in res_json['content']['videoChats']:
        try:
            ### -------- Raw json handling starts -------- ###
            extras  = "" if not chat['extras'] else json.loads(chat['extras'])    # contains extra infos of the chat such as donation amount, gift type, emotes(url of image), etc
            profile = "" if not chat['profile'] else json.loads(chat['profile'])  # this is Null/None if user is anonymous
            
            chat_user_device_os     = extras["osType"] if extras and "osType" in extras else ""
            chat_emojis             = extras["emojis"] if extras and "emojis" in extras else {} 


            chat_user_nickname      = profile['nickname'] if profile else ""
            chat_user_channel_id    = profile['userIdHash'] if profile else ""
            chat_message_time       = int(chat['playerMessageTime'])
            chat_content            = '\"' + chat['content'].replace("\n", " ").replace('\x00', "") + '\"'  # newlines and nul value seem to appear somethimes
            chat_message_type_code  = chat['messageTypeCode']
            chat_donation_amount    = int(extras['payAmount']) if chat['messageTypeCode'] == 10 else 0      # type: ignore -> payAmount will always be integer if the message type is donation
            
            if chat['messageTypeCode'] not in set((1, 10, 11, 12, 30)):      # @TODO make this a set of enum
                logger.warning("Unkown messageTypeCode encountered: %d", chat['messageTypeCode'])
                for k, v in chat.items():
                    logger.info("%s: %s", k, v)
            ### -------- Raw json handling ends -------- ###

            chat_info = ChatInfo(chat_user_nickname     = chat_user_nickname,
                                chat_user_channel_id    = chat_user_channel_id,
                                chat_video_id           = video_number,
                                chat_message_time       = chat_message_time,
                                chat_content            = chat_content,
                                chat_message_type_code  = chat_message_type_code,
                                chat_donation_amount    = chat_donation_amount,
                                chat_user_device_os     = chat_user_device_os,
                                chat_emojis             = chat_emojis,)
            user_info = UserInfo(chat_user_nickname, chat_user_channel_id)
            users.add(user_info)
            chats.append(chat_info)
            
        except KeyError as ke:
            logger.warning("Key Error Occured: %s", ke)
            for k, v in chat.items():
                logger.info("%s: %s", k, v)
                
    return chats, users


def write_video_info_to_csv(video_info: VideoInfo):
    """Saves specific loaded vods on csv file."""
    video_csv_path = Path("Raw Data\\videos.csv")
    
    if not video_csv_path.exists():
        with open(video_csv_path, "w", newline="", encoding="utf-8") as f:
            csv_writer = csv.DictWriter(f, fieldnames=VIDEOS_CSV_HEADER)
            csv_writer.writeheader()
        
    with open(video_csv_path, "a", newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=VIDEOS_CSV_HEADER)
        csv_writer.writerow(video_info.get_dict())


def write_vod_chats_to_csv(streamer_name: str, video_number: int, video_chats: list[ChatInfo]):
    """Given streamer and vod chats, initializes (if necessary) and appends the chat to corresponding csv."""
    chat_csv_path = Path(f"Raw Data\\Chats\\{streamer_name}_{video_number}_chats.csv")
    
    if not chat_csv_path.exists():
        with open(chat_csv_path, 'w', newline="", encoding="utf-8") as f:
            csv_writer = csv.DictWriter(f, fieldnames=CHATS_CSV_HEADER)
            csv_writer.writeheader()
    
    with open(chat_csv_path, 'a', newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=CHATS_CSV_HEADER)
        for chat_info in video_chats:
            csv_writer.writerow(chat_info.get_dict())

if __name__ == "__main__":
    pass
    # what if the user in 1 stream appear in another stream? how do I get
    # index on the user name 
    # check user name if they exist