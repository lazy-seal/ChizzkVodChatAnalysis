# Chizzk VOD Analysis
치지직에서 활동하는 스트리머 방송 다시보기의 채팅을 스크랩하여 데이터베이스에 저장할 수 있는 프래임워크입니다.

# TODO:
- implement:
    - api call timout
    - DatabaseManagement.py: figure out asynchronous way of inputting data
        chat, videos, users: straight insert into
        chats references videos, users
        videos references users (streamers)
        users does not reference
    - run.py
        - (db) while going through chat, count how many chat, donation, and active users are in the video
        - save user.csv while doing the initial fetching?
    - eventaully figure out way to move the data directly from api to db without going through chat

    -  for every new chat file gathered
- centeralize api urls to InfoDataObjects.py (or should I?)
- Should I consider making Crawler.py into a class? or not? (since most of them uses the same httpx client)

## TODO Ideas for Data anyalysis
### Doesn't need Pre-Processing
- Engagement metrics: follower count to average chatting user (video전체 시청자 수를 알아낼 수가 없다) ratio, messages per minute, 스트리머별 가장 '핫'한 다시보기 등
    - Getting releavant information for individual videos:
    ```SQL
    SELECT video_chat_count, video_user_count, video_duration FROM videos
    ``` 
    - Streamer Specific Analysis:
    ```SQL
    WITH streamer AS (
        SELECT video_streamer_id, 
            SUM(video_duration) AS total_video_duration
            SUM(video_chat_count) AS total_chat_count
            SUM(video_user_count) AS total_chatter_count
            SUM(video_total_donation_amount) as total_donation_amount
        FROM videos
        GROUP BY video_streamer_id 
    ), average_chats_per_chatter AS (
        SELECT total_chat_amount / total_chatter_count
        FROM streamer
    ), average_chats_per_minute AS (
        SELECT total_chat_amount / total_video_duration
        FROM streamer
    )
    SELECT users.user_nickname, 
        streamer.average_chats_per_chatter,
        streamer.average_chats_per_minute
    FROM users, streamer
    ```
- Graph on chat frequency during the timeline of the video (chat frequency analysis)
    - chat.chat_message_time을 1~5분 단위로 묶어서 video_duration을 기준으로 그래프
- Chat rate per user (within the people who actually chat)
- 시청자-specific metrics:
    - The "Superfans" who chatted most in the stream
    - how many users chat in different streams
- category/tag specific metrics:
    - participation rate of chat given category or tags of stream

### Needs Pre-processing:
- Word Frequency + Wordcloud: comparative analysis between streamers, streaming categories
- Sentiment Analysis: pos/neg, toxisity, horniness, etc

### Could be both:
- Analysis in relation to Streaming lifecycle: early, middle, end
- Streamer Similarity Clustering: viewer overlap, word usage patterns, topics

### Other Ideas:
- Guessing game of what streamer's data it is (like a chat frequency, or any other metric that I provided)
    - Video Hook: "이 스트리머는 {각종 흥미로운 통계 등}. 누구일까요?"
- 스텔라이브 전부 있음: 스텔라이브 분석?
    사장(강지) vs 직원
- 버튜버 vs 캠방?
- Phone viwer vs PC viewer?
- 

