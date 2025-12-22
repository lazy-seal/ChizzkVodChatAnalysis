-- I'm not sure if this is necessary in my situation though
-- maybe rebuild after bunch of new videos added?

ALTER INDEX idx_user_id ON users REBUILD;
ALTER INDEX idx_video_id ON videos REBUILD;
ALTER INDEX idx_chats_per_streamer ON chats REBUILD;
ALTER INDEX idx_chats_per_video ON chats REBUILD;