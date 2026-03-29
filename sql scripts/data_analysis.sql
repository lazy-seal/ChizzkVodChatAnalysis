SELECT * FROM users;
SELECT * FROM chats;
SELECT * FROM videos;

SELECT AVG(video_chat_count) FROM videos;

SELECT chat_emojis FROM chats LIMIT 500;

SELECT count(*), chat_user_device_os as os FROM chats group by chat_user_device_os;

-- timeframe block chats
SELECT
    (chat_message_time / 60000) AS vod_timestamp,
    COUNT(*) AS message_count
FROM 
    chats
WHERE
	chat_video_id = 11061865
GROUP BY 
    (chat_message_time / 60000)
ORDER BY vod_timestamp;
	
-- 스트리머별 통계
SELECT 
	u.user_nickname AS "스트리머", 
	SUM(v.video_chat_count) AS "총 채팅수", 
	AVG(v.video_chat_count) AS "평균 채팅수",
	SUM(v.video_chat_count) / (SUM(v.video_duration) / 60) AS "채팅 화력 (chats per minutes)",
	SUM(v.video_total_donation_amount) AS "총 도네", 
	SUM(v.video_total_donation_amount) / (SUM(v.video_duration) / 360) AS "도네 화력 (donation per hours)",
	AVG(v.video_total_donation_amount) AS "평균 도네",
	AVG(v.video_active_user_count) AS "평균 채팅 유저"
FROM videos as v, users as u
WHERE v.video_streamer_id = u.user_id
GROUP BY v.video_streamer_id, u.user_id
ORDER BY "채팅 화력 (chats per minutes)" DESC;

-- 스트리머별 자주 쓰이는 이모티콘
SELECT 
	u.user_id,
	u.user_nickname,
	count(v.video_id) as num_replays,
	-- ARRAY_AGG(v.video_id) as replay_list
	ARRAY_AGG(
		SELECT
			emj.key,
			emj.value,
			count(emj) as count
		LATERAL jsonb_each(c.chat_emojis) as emj
	) AS emojis
FROM users as u
INNER JOIN videos v ON u.user_id = v.video_streamer_id
INNER JOIN chats c ON v.video_id = c.chat_video_id
GROUP BY u.user_id;

-- 스트리머, 이코티콘 총 사용량, 이모티콘 가짓수, 이모티콘 키
SELECT 
        -- u.user_id,
        u.user_nickname,
        -- (emj.value)::int AS usage_count
		COUNT(emj.key) as total_emojis_count,
		COUNT(DISTINCT emj.key) as distinct_emojis_count,
		ARRAY_AGG(DISTINCT emj.key) as emojis_key
    FROM users u
    INNER JOIN videos v ON u.user_id = v.video_streamer_id
    INNER JOIN chats c ON v.video_id = c.chat_video_id
    CROSS JOIN LATERAL jsonb_each(c.chat_emojis) AS emj
	GROUP BY u.user_id;

-- 유저별 통계
-- top 100으로 끊자 (유저가 너무 많음)
-- 도네로 정렬
SELECT 
	u.user_nickname as 치수, 
	COUNT(c.chat_id) AS 채팅_수,
	SUM(c.chat_donation_amount) AS 총_도네
FROM chats AS c, users AS u
WHERE c.chat_user_id = u.user_id
GROUP BY chat_user_id, u.user_id
ORDER BY 총_도네 DESC
LIMIT 500;

-- 채팅_수로 정렬
SELECT 
	u.user_nickname as 치수, 
	COUNT(c.chat_id) AS 채팅_수,
	SUM(c.chat_donation_amount) AS 총_도네
FROM chats AS c, users AS u
WHERE c.chat_user_id = u.user_id
GROUP BY chat_user_id, u.user_id
ORDER BY 채팅_수 DESC
LIMIT 500;

-- (추가) 스트리머별 가장 많이 채팅을 친 유저들

-- 영상 카테고리별 통계
SELECT
	v.video_category AS "카테고리",
	COUNT(v.video_id) AS "총 영상 수",
	SUM(v.video_total_donation_amount) AS "총 도네",
	SUM(v.video_total_donation_amount) / (SUM(v.video_duration) / 360) AS "도네 화력 (donation per hours)",
	SUM(v.video_chat_count) AS "총 채팅 수",
	SUM(v.video_chat_count) / (SUM(v.video_duration) / 60) AS "채팅 화력 (chats per minutes)",
	AVG(v.video_duration) AS "평균 영상 길이"
FROM videos as v
GROUP BY v.video_category;

-- OS별 통계
SELECT 
	c.chat_user_device_os as "OS", 
	COUNT(c.chat_id) AS "총 채팅 수",
	COUNT(c.user_id) AS "총 (채팅 치는) 유저 수",
	COUNT(c.chat_id) / (SUM(v.video_dutation) / 60) AS "채팅 화력",
	SUM(c.chat_donation_amount) AS "총 도네이션",
	SUM(c.chat_donation_amount) / (SUM(v.video_duration) / 360) AS "도네 화력"
FROM chats AS c, videos as v
WHERE c.chat_video_id = v.video_id
GROUP BY c.chat_user_device_os
ORDER BY "총 채팅 수" DESC
LIMIT 500;
