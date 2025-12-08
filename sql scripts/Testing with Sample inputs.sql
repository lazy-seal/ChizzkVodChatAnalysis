
-- Input sample data
WITH new_user AS (
	INSERT INTO users (user_channel_id,
						user_nickname)
	VALUES ('f2e88212cb3ec19ec36f1f59dd04b68d','채호링족욕기함민재님')
	RETURNING user_id
),
new_video AS (
	INSERT INTO videos (video_streamer_id, 
						video_duration)
	SELECT user_id, 400
	FROM new_user
	RETURNING video_id
)
INSERT INTO chats (chat_user_id, 
				chat_video_id, 
				chat_message_time, 
				chat_content,
				chat_message_type_code,
				chat_extras)
	SELECT new_user.user_id,
		new_video.video_id, 
		35769, 
		'{:niniaoGmsemf:}{:niniaoGmsemf:}{:niniaoGmsemf:}',
		1,
		'{"osType":"AOS","chatType":"STREAMING","streamingChannelId":"f00f6d46ecc6d735b96ecf376b9e5212","emojis":{"niniaoGmsemf":"https:\/\/nng-phinf.pstatic.net\/glive\/subscription\/emoji\/f00f6d46ecc6d735b96ecf376b9e5212\/1\/niniaoGmsemf_1711025908535.gif"},"extraToken":"ES\/ZXCjf44zcfGMhmhc24MgI58itcCponvGhfHqFRZuAxQ6+ZVQ\/VsabK4KsBvw1GSJzUCGSXsSNSZthXPJIpQ=="}'
	FROM new_user, new_video;


SELECT * FROM users; 
SELECT * FROM videos;
SELECT * FROM chats;

-- Get rid of the sample data
-- TRUNCATE chats, videos, users RESTART IDENTITY CASCADE;

