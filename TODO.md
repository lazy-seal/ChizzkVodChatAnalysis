# TODO implementation:
- implement:
    - Go over comments and docstrings: update them
    - make init.py
    - extract "extra" to save space?
        - at least erase the ones I don't need like tokens and stuff
    - db to csv, https to csv
    - Update Testing.py 
    - Error handling:
        - when no data was received 
    - centeralize api urls to InfoDataObjects.py (or should I?)

# TODO Ideas for Data anyalysis
## Doesn't need Pre-Processing
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
- Chat rate per user (within the people who actually chat)
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

## Future Ideas:
- Streamer Bot (sort of)
    - Data gained by chat with the current program
    - plus, for each video, see if the replay is uploaded on youtube
    - if so, download auto-gen subtitles for it
    - match the time of the chat with the replay
    - train the llm