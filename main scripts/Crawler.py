import json
import csv
from pathlib import Path
import logging
from pprint import pprint
import httpx
import asyncio
import pandas as pd
from InfoDataObjects import VideoInfo, ChatInfo, UserInfo, StreamerInfo, VIDEOS_CSV_HEADER, CHATS_CSV_HEADER, STREAMERS_CSV_HEADER, USERS_CSV_HEADER

# I don't really need a lock on async processes?
# I just need to make sure coroutine closes the file
# when it suspends itself
# users_csv_lock = asyncio.Lock()
# streamers_csv_lock = asyncio.Lock()
# videos_csv_lock = asyncio.Lock()

with open("Private//private.json", encoding="utf-8") as f:
        private_file = json.load(f)
        HEADERS = {"User-Agent": "Mozilla/5.0",
                   "Client-ID": private_file['Client-ID']}

logger = logging.getLogger(__name__)
logging.basicConfig(filename='Crawler.log', encoding='utf-8', level=logging.INFO)

async def update_user_info(streamers_only = False):
    """Updates the streamer info in users.csv"""
    if streamers_only:
        csv_path = Path("Raw Data\\streamers.csv")
    else:
        csv_path = Path("Raw Data\\users.csv")
    
    if not csv_path.exists():
        logger.info(f"Update Not possible: {csv_path} does not exist")
        return

    updated_users: list[UserInfo]           = []
    updated_streamers: list[StreamerInfo]   = []
    
    df = pd.read_csv(csv_path, encoding="utf-8")
    
    tasks = []
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            for channel_id in df["streamer_channel_id" if streamers_only else "user_channel_id"]:
                tasks.append(tg.create_task(load_user_info(client, channel_id)))

    for user_info in [task.result() for task in tasks]:
        if user_info.user_channel_type == "STREAMING":
            updated_streamers.append(StreamerInfo(user_info.user_nickname, 
                                                user_info.user_channel_id))
        updated_users.append(user_info)

    save_user_info_to_csv(updated_users)


async def load_user_info(client: httpx.AsyncClient, user_channel_id: str) -> UserInfo:
    """Makes asyncronuous http reqeust to Chzzk api to get user data based on their channel id"""
    url = f"https://api.chzzk.naver.com/service/v1/channels/{user_channel_id}"
    res = await client.get(url=url, headers=HEADERS)
    
    # knwon responses:
    # 200: great
    # 500/9002: "이 채널은 네이버 운영 정책을 위반하여 일시적으로 이용할 수 없습니다."
    
    if res.status_code not in (200, 500):
        raise ConnectionError(f"the api call was not successful:{res}")
    
    content = res.json()['content']
    
    if content['channelName'] == "(알 수 없음)":
        pprint(content)
    
    user_info = UserInfo(
        user_nickname               = content['channelName'],
        user_channel_id             = content['channelId'],
        user_channel_description    = content['channelDescription'].replace("\n", " "),
        user_follower_count         = content['followerCount'],
        user_channel_type           = content['channelType'],       # "NORMAL" or "STREAMING"
    )
    return user_info

def save_user_info_to_csv(user_info_list: list[UserInfo]):
    """
    Saves MULTIPLE users info into the csv file.
    Any streamers in user_info_list is also saved to streamers.csv
    """
    users_csv_path = Path("Raw Data\\users.csv")
    streamers_csv_path = Path("Raw Data\\streamers.csv")
    streamer_info_list = []
    
    if not users_csv_path.exists():
        with open(users_csv_path, "w", encoding="utf-8") as f:
            csv_writer = csv.DictWriter(f, USERS_CSV_HEADER)
            csv_writer.writeheader()
    
    if not streamers_csv_path.exists():
        with open(streamers_csv_path, "w", encoding="utf-8") as f:
            csv_writer = csv.DictWriter(f, USERS_CSV_HEADER)
            csv_writer.writeheader()

    ### Save User Data Starts ###
    users_df = pd.read_csv(users_csv_path, encoding="utf-8")
    for user_info in user_info_list:
        if user_info.user_channel_type == "STREAMING":
            streamer_info_list.append(StreamerInfo(user_info.user_nickname, 
                                                user_info.user_channel_id))
        user = users_df["user_channel_id"] == user_info.user_channel_id
        if user.any():
            users_df.loc[users_df["user_channel_id"] == user_info.user_channel_id, 
                         USERS_CSV_HEADER] = list(user_info)
        else:
            users_df.loc[len(users_df)] = list(user_info)
    users_df.to_csv(users_csv_path, index=False, encoding="utf-8")
    ### Save User Data Ends ###
    
    
    ### Save Streamer Data Starts ###
    if streamer_info_list:
        streamers_df = pd.read_csv(streamers_csv_path, encoding="utf-8")
        for streamer_info in streamer_info_list:
            streamer = users_df["user_channel_id"] == streamer_info.streamer_channel_id
            if streamer.any():
                streamers_df.loc[streamers_df["streamer_channel_id"] == streamer_info.streamer_channel_id, 
                                 STREAMERS_CSV_HEADER] = list(streamer_info)
            else:
                streamers_df.loc[len(streamers_df)] = list(streamer_info)
        streamers_df.to_csv(streamers_csv_path, index=False, encoding="utf-8")
    ### Save Streamer Data Edns ###


async def load_video_info(client: httpx.AsyncClient, streamer_name, streamer_channel_id, n_videos_to_load=50) -> list[VideoInfo]:
    """Performs a api call to loads and returns a list of vod replay information of the streamer.
    
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
    
    for video in res_json["content"]["data"]:
        video_info = VideoInfo(
            video_streamer_name         = streamer_name,
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
    # random.shuffle(self.vod_numbers)
    return vods

async def load_chat_data(client: httpx.AsyncClient, video_number: int, message_time: int) -> list[ChatInfo]:
    """Performs an api request to chzzk web api, returns results of the request
    
    Parameters:
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
    response = await client.get(url=url, headers=HEADERS)
    res_json = response.json()
    chats: list[ChatInfo] = []
    
    if response.status_code != 200 or len(res_json['content']['videoChats']) == 0:
        logger.info("Fetch Finished on vid %d: status_code: %d", video_number, response.status_code)
        return []

    for chat in res_json['content']['videoChats']:
        try:
            ### -------- Raw json handling starts -------- ###
            extras  = "" if not chat['extras'] else json.loads(chat['extras'])    # contains extra infos of the chat such as donation amount, gift type, emotes(url of image), etc
            profile = "" if not chat['profile'] else json.loads(chat['profile'])  # this is Null/None if user is anonymous

            chat_user_nickname      = "" if not profile else profile['nickname']
            chat_user_channel_id    = "" if not profile else profile['userIdHash']
            chat_message_time       = int(chat['playerMessageTime'])
            chat_content            = '\"' + chat['content'].replace("\n", " ") + '\"'  # adds \" to make sure  comma on chat won't affect csv formatting
            chat_message_type_code  = int(chat['messageTypeCode'])
            chat_donation_amount    = 0 if chat['messageTypeCode'] != 10 else int(extras['payAmount']) # type: ignore -> payAmount will always be integer if the message type is donation
            chat_extras             = "" if not chat['extras'] else '\"' + chat['extras'].replace("\n", " ") + '\"'    # same reason to add \"
            
            if chat['messageTypeCode'] == 10:
                chat_donation_amount = int(extras['payAmount']) # type: ignore
            
            if chat['messageTypeCode'] not in set((1, 10, 11, 12, 30)):      # @TODO make this a set of enum
                logger.warning("Unkown messageTypeCode encountered: %d", chat['messageTypeCode'])
                for k, v in chat.items():
                    logger.info("%s: %s", k, v)
            ### -------- Raw json handling ends -------- ###

            chat_info = ChatInfo(chat_user_nickname     = chat_user_nickname,
                                chat_user_channel_id    = chat_user_channel_id,
                                chat_message_time       = chat_message_time,
                                chat_content            = chat_content,
                                chat_message_type_code  = chat_message_type_code,
                                chat_donation_amount    = chat_donation_amount,
                                chat_extras             = chat_extras)
            chats.append(chat_info)
            
        except KeyError as ke:
            logger.warning("Key Error Occured: %s", ke)
            for k, v in chat.items():
                logger.info("%s: %s", k, v)
                
    return chats


def save_video_info_to_csv(video_info: VideoInfo):
    """Saves specific loaded vods on csv file."""
    video_csv_path = Path("Raw Data\\videos.csv")
    
    if not video_csv_path.exists():
        with open(video_csv_path, "w", newline="", encoding="utf-8") as f:
            csv_writer = csv.DictWriter(f, fieldnames=VIDEOS_CSV_HEADER)
            csv_writer.writeheader()
        
    with open(video_csv_path, "a", newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=VIDEOS_CSV_HEADER)
        csv_writer.writerow(video_info.get_dict())


def save_vod_chats_to_csv(streamer_name: str, video_number: int, video_chats: list[ChatInfo]):
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
    with open("TEST\\TEST.csv", "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=CHATS_CSV_HEADER)
        csv_writer.writeheader()
    
    # what if the user in 1 stream appear in another stream? how do I get
    # index on the user name 
    # check user name if they exist