CREATE TABLE users (
	username VARCHAR(100) NOT NULL,
	email	 VARCHAR(100) NOT NULL,
	password VARCHAR(60) NOT NULL,
	user_id	 BIGSERIAL,
	PRIMARY KEY(user_id)
);

CREATE TABLE consumer (
	address	 VARCHAR(300),
	subscription	 BOOL,
	telephone	 BIGINT,
	users_user_id BIGINT,
	PRIMARY KEY(users_user_id)
);

CREATE TABLE premium (
	period		 VARCHAR(30) NOT NULL,
	end_date		 DATE NOT NULL,
	subscription_id	 BIGSERIAL,
	price			 SMALLINT NOT NULL,
	consumer_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(subscription_id)
);

CREATE TABLE administrator (
	number_cards	 BIGINT,
	users_user_id BIGINT,
	PRIMARY KEY(users_user_id)
);

CREATE TABLE pre_paid_card (
	card_id			 VARCHAR(18),
	card_price			 INTEGER NOT NULL,
	limit_date			 DATE NOT NULL,
	administrator_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(card_id)
);

CREATE TABLE artist (
	name			 VARCHAR(100) NOT NULL,
	administrator_users_user_id BIGINT NOT NULL,
	users_user_id		 BIGINT,
	PRIMARY KEY(users_user_id)
);

CREATE TABLE playlist (
	playlist_name		 VARCHAR(100) NOT NULL,
	visibility		 VARCHAR(20) NOT NULL,
	playlist_id		 BIGSERIAL,
	consumer_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(playlist_id)
);

CREATE TABLE album (
	album_name	 VARCHAR(100) NOT NULL,
	release_date	 VARCHAR(100),
	album_id		 BIGSERIAL,
	record_label_name VARCHAR(100),
	PRIMARY KEY(album_id)
);

CREATE TABLE song (
	ismn		 BIGSERIAL,
	name		 VARCHAR(100) NOT NULL,
	genre		 VARCHAR(100) NOT NULL,
	release_date	 DATE,
	duration		 INTEGER NOT NULL,
	record_label_name	 VARCHAR(100),
	artist_users_user_id BIGINT,
	PRIMARY KEY(ismn)
);

CREATE TABLE record_label (
	name VARCHAR(100),
	PRIMARY KEY(name)
);

CREATE TABLE coment (
	comment_id		 BIGSERIAL,
	texto			 TEXT NOT NULL,
	consumer_users_user_id BIGINT NOT NULL,
	PRIMARY KEY(comment_id)
);

CREATE TABLE stream (
	id_stream		 BIGINT,
	stream_date		 TIMESTAMP NOT NULL,
	song_ismn		 BIGINT NOT NULL,
	consumer_users_user_id BIGINT NOT NULL
);

CREATE TABLE coment_coment (
	coment_comment_id	 BIGINT,
	coment_comment_id1 BIGINT NOT NULL,
	PRIMARY KEY(coment_comment_id)
);

CREATE TABLE coment_song (
	coment_comment_id BIGINT,
	song_ismn	 BIGINT,
	PRIMARY KEY(coment_comment_id,song_ismn)
);

CREATE TABLE artist_record_label (
	artist_users_user_id BIGINT,
	record_label_name	 VARCHAR(100),
	PRIMARY KEY(artist_users_user_id,record_label_name)
);

CREATE TABLE song_playlist (
	song_ismn		 BIGINT,
	playlist_playlist_id BIGINT,
	PRIMARY KEY(song_ismn,playlist_playlist_id)
);

CREATE TABLE album_song (
	album_album_id BIGINT,
	song_ismn	 BIGINT,
	PRIMARY KEY(album_album_id,song_ismn)
);

CREATE TABLE artist_song (
	artist_users_user_id BIGINT,
	song_ismn		 BIGINT,
	PRIMARY KEY(artist_users_user_id,song_ismn)
);

CREATE TABLE artist_album (
	artist_users_user_id BIGINT NOT NULL,
	album_album_id	 BIGINT,
	PRIMARY KEY(album_album_id)
);

CREATE TABLE pre_paid_card_premium (
	pre_paid_card_card_id	 VARCHAR(18),
	premium_subscription_id BIGINT,
	PRIMARY KEY(pre_paid_card_card_id,premium_subscription_id)
);

ALTER TABLE users ADD UNIQUE (username, email, password);
ALTER TABLE consumer ADD CONSTRAINT consumer_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE premium ADD CONSTRAINT premium_fk1 FOREIGN KEY (consumer_users_user_id) REFERENCES consumer(users_user_id);
ALTER TABLE premium ADD CONSTRAINT constraint_Periodo_preco CHECK ((Period='month' AND Price=7) OR (Period='quarter'  AND Price=21) OR (Period='semester' AND Price=42));
ALTER TABLE administrator ADD CONSTRAINT administrator_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE pre_paid_card ADD CONSTRAINT pre_paid_card_fk1 FOREIGN KEY (administrator_users_user_id) REFERENCES administrator(users_user_id);
ALTER TABLE artist ADD UNIQUE (name);
ALTER TABLE artist ADD CONSTRAINT artist_fk1 FOREIGN KEY (administrator_users_user_id) REFERENCES administrator(users_user_id);
ALTER TABLE artist ADD CONSTRAINT artist_fk2 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE playlist ADD CONSTRAINT playlist_fk1 FOREIGN KEY (consumer_users_user_id) REFERENCES consumer(users_user_id);
ALTER TABLE playlist ADD CONSTRAINT constraint_publico_privada CHECK (Visibility='public' OR Visibility='private' );
ALTER TABLE album ADD UNIQUE (album_name);
ALTER TABLE coment ADD CONSTRAINT coment_fk1 FOREIGN KEY (consumer_users_user_id) REFERENCES consumer(users_user_id);
ALTER TABLE stream ADD UNIQUE (id_stream);
ALTER TABLE stream ADD CONSTRAINT stream_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE stream ADD CONSTRAINT stream_fk2 FOREIGN KEY (consumer_users_user_id) REFERENCES consumer(users_user_id);
ALTER TABLE coment_coment ADD CONSTRAINT coment_coment_fk1 FOREIGN KEY (coment_comment_id) REFERENCES coment(comment_id);
ALTER TABLE coment_coment ADD CONSTRAINT coment_coment_fk2 FOREIGN KEY (coment_comment_id1) REFERENCES coment(comment_id);
ALTER TABLE coment_song ADD CONSTRAINT coment_song_fk1 FOREIGN KEY (coment_comment_id) REFERENCES coment(comment_id);
ALTER TABLE coment_song ADD CONSTRAINT coment_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE artist_record_label ADD CONSTRAINT artist_record_label_fk1 FOREIGN KEY (artist_users_user_id) REFERENCES artist(users_user_id);
ALTER TABLE artist_record_label ADD CONSTRAINT artist_record_label_fk2 FOREIGN KEY (record_label_name) REFERENCES record_label(name);
ALTER TABLE song_playlist ADD CONSTRAINT song_playlist_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE song_playlist ADD CONSTRAINT song_playlist_fk2 FOREIGN KEY (playlist_playlist_id) REFERENCES playlist(playlist_id);
ALTER TABLE album_song ADD CONSTRAINT album_song_fk1 FOREIGN KEY (album_album_id) REFERENCES album(album_id);
ALTER TABLE album_song ADD CONSTRAINT album_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk1 FOREIGN KEY (artist_users_user_id) REFERENCES artist(users_user_id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE artist_album ADD CONSTRAINT artist_album_fk1 FOREIGN KEY (artist_users_user_id) REFERENCES artist(users_user_id);
ALTER TABLE artist_album ADD CONSTRAINT artist_album_fk2 FOREIGN KEY (album_album_id) REFERENCES album(album_id);
ALTER TABLE pre_paid_card_premium ADD CONSTRAINT pre_paid_card_premium_fk1 FOREIGN KEY (pre_paid_card_card_id) REFERENCES pre_paid_card(card_id);
ALTER TABLE pre_paid_card_premium ADD CONSTRAINT pre_paid_card_premium_fk2 FOREIGN KEY (premium_subscription_id) REFERENCES premium(subscription_id);