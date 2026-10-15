# TODO implementation:
- 스트리머 목록 정리

# TODO Ideas for Data anyalysis
## Doesn't need Pre-Processing
- 최대 효율이 나오는 방송 시간 (average/median income per total video duration)
- 시청 기기 OS별로 나뉘는 방송 시청 성향
	- 기기별 시청 방송 테그 / 카테고리 / 도네이션 양 등
- 방송 평균 시간이 가장 긴 스트리머
- 가장 채팅 화력이 센 스트리머
- 가장 채팅을 많이 친 유저
- 가장 도네를 많이 한 유저
- 가장 많이 사용된 이모티콘 top 10
- 시청자층이 겹치는 스트리머들
- Chat rate per user (within the people who actually chat)
    - The "Superfans" who chatted most in the stream
    - how many users chat in different streams
- category/tag specific metrics:
    - participation rate of chat given category or tags of stream


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
