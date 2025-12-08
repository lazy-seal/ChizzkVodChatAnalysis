DROP TABLE IF EXISTS chats, videos, users CASCADE;

CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	user_channel_id TEXT UNIQUE,
	user_nickname TEXT UNIQUE,
	user_follower_count INTEGER,
	user_different_names TEXT[],
	user_channel_type TEXT, -- either "STREAMING" or "NORMAL", plus maybe something else I haven't seen
);

CREATE TABLE videos(
	video_id SERIAL PRIMARY KEY,
	video_streamer_id INTEGER REFERENCES users(user_id),
	video_number INTEGER UNIQUE NOT NULL,
	video_title TEXT,
	video_duration INTEGER, -- video_duration is in seconds
	video_tags TEXT[],
	video_category_type TEXT,
	video_category TEXT, 
	video_publish_date TEXT,
	video_chat_count INTEGER,
	video_total_donation_amount INTEGER,
	video_active_user_count INTEGER
);

CREATE TABLE chats(
	chat_id SERIAL PRIMARY KEY,
	chat_user_id INTEGER REFERENCES users(user_id) NOT NULL,
	chat_video_id INTEGER REFERENCES videos(video_id) NOT NULL,
	chat_message_time INTEGER NOT NULL,
	chat_content TEXT NOT NULL,
	chat_message_type_code SMALLINT NOT NULL,
	chat_donation_amount INTEGER,
	chat_extras JSONB
);