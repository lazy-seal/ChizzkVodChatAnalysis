# TODO implementation:
- implement:
    - Continue Debugging testing
        - "TypeError: tuple indices must be integers or slices, not str"
    - instead of doing api call for each and every user, I should just use the info given by chat data
    - Error handling:
        - api call timout
        - when no data was received: maybe return empty DataInfo namedtuple?
    - run.py
        - (db) while going through chat, count how many chat, donation, and active users are in the video
    - eventaully figure out way to move the data directly from api to db (without csv in the middle)
- centeralize api urls to InfoDataObjects.py (or should I?)

# TODO Ideas for Data anyalysis
## Doesn't need Pre-Processing
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

## Needs Pre-processing:
- Word Frequency + Wordcloud: comparative analysis between streamers, streaming categories
- Sentiment Analysis: pos/neg, toxisity, horniness, etc
    - sentiment analysis graphing (average video)

## Could be both:
- Analysis in relation to Streaming lifecycle: early, middle, end
- Streamer Similarity Clustering: viewer overlap, word usage patterns, topics

## Other Ideas:
- Guessing game of what streamer's data it is (like a chat frequency, or any other metric that I provided)
    - Video Hook: "이 스트리머는 {각종 흥미로운 통계 등}. 누구일까요?"
- 버튜버 vs 캠방?

## Future Ideas:
- Streamer Bot (sort of)
    - Data gained by chat with the current program
    - plus, for each video, see if the replay is uploaded on youtube
    - if so, download auto-gen subtitles for it
    - match the time of the chat with the replay
    - train the llm