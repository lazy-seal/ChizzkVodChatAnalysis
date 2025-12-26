DROP TABLE IF EXISTS chats, videos, users CASCADE;

CREATE TABLE users(
	user_id TEXT PRIMARY KEY, -- Note that this is text
	user_nickname TEXT
);

CREATE TABLE videos(
	video_id INTEGER PRIMARY KEY,	-- video_number
	video_streamer_id TEXT REFERENCES users(user_id),
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
	chat_user_id TEXT REFERENCES users(user_id) NOT NULL, -- There is a case in which this is just empty string, this is the anonymous donation or System Message?
	chat_video_id INTEGER REFERENCES videos(video_id) NOT NULL,
	chat_message_time INTEGER NOT NULL,
	chat_content TEXT NOT NULL,
	chat_message_type_code SMALLINT NOT NULL,
	chat_donation_amount INTEGER,
	chat_extras JSONB
);

CREATE UNIQUE INDEX idx_user_id ON users (user_id);
CREATE UNIQUE INDEX idx_video_id ON videos (video_id);
CREATE INDEX idx_chats_per_streamer ON chats (chat_user_id);
CREATE INDEX idx_chats_per_video ON chats (chat_video_id);