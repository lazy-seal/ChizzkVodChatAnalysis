# TODO implementation:
- implement:
    - db to csv, https to csv
    - Update Testing.py 

# TODO Ideas for Data anyalysis
## Doesn't need Pre-Processing
    - Getting releavant information for individual videos:
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