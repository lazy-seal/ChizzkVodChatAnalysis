SELECT * FROM users;
SELECT * FROM chats WHERE chat_user_id = 'cc8f88e939080b37e78b87fd0172248c';
SELECT * FROM videos;

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
WHERE v.video_streamer_id = u.user_id -- I should add date-checking clause
GROUP BY v.video_streamer_id, u.user_id;

-- 유저별 통계
-- top 100으로 끊자 (유저가 너무 많음)
SELECT 
	u.user_nickname as "치수", 
	COUNT(c.chat_id) AS "채팅 수",
	SUM(c.chat_donation_amount) AS "총 도네 수"
FROM chats AS c, users AS u
WHERE c.chat_user_id = u.user_id
GROUP BY chat_user_id, u.user_id;

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
