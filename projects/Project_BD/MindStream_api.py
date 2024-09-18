import flask
import psycopg2
from flask import Flask, json
import jwt
import logging
import traceback
import secrets
import datetime
from dateutil.relativedelta import relativedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from psycopg2 import errors
import random
import bcrypt

jwt_secret = secrets.token_urlsafe(32)
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "50709a768b73ec9ecb8d8ff6804e62"
app.config['JWT_SECRET_KEY'] = jwt_secret
jwt = JWTManager(app)


def db_connection():  # dados para conexão à base de dados
    db = psycopg2.connect(
        user='postgres',
        password='Supreme_698',
        host="localhost",
        port='5432',
        database='Streaming'
    )
    return db


@app.route('/')
def landing_page():
    return """Bem-vindo!<br/>
    <br/>
    <br/>
    <br/>
    <br/>
    <br/>
    """


@app.route('/dbproj/first_admin', methods=['PUT'])
def create_first_admin():
    conn = db_connection()
    cur = conn.cursor()

    username = "admin"
    email = "admin@gmail.com"
    password = "securepassword"
    password = password.encode('utf-8')

    # Verifica se existe o admin na base de dados, se não cria
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result is None:
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        insert_admin_user = """INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING user_id;"""
        cur.execute(insert_admin_user, (username, email, hashed_password.decode('utf-8'),))
        user_id = cur.fetchone()[0]

        insert_administrador = """INSERT INTO administrator (number_cards, users_user_id) VALUES (%s, %s)"""
        cur.execute(insert_administrador, (0, user_id,))
        conn.commit()

        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": user_id})

    else:
        cur.close()
        conn.close()
        return flask.jsonify({"status": 400, "results": "First admin already inserted!"})



@app.route('/dbproj/user', methods=['POST'])
def register_user():
    data = flask.request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password').encode('utf-8')  # convert string to bytes

    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    try:
        conn = db_connection()
        cur = conn.cursor()
        insert = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING user_id;"
        cur.execute(insert, (username, email, hashed_password.decode('utf-8'),))  # Convert bytes back to string for storage
        user_id = cur.fetchone()[0]

        insert_consumer = "INSERT INTO consumer (users_user_id) VALUES (%s);"
        cur.execute(insert_consumer, (user_id,))

        conn.commit()
        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": user_id})

    except Exception as e:
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        conn = db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM administrator WHERE users_user_id = %s;", (user_id,))
            admin_user = cur.fetchone()
            if admin_user is None:
                return flask.jsonify({"status": 403, "errors": "User is not an administrator"}), 403
            return f(*args, **kwargs)
        except (Exception, errors.DatabaseError) as error:
            print(f"Error: {error}")
            conn.rollback()
            cur.close()
            return flask.jsonify({"status": 500, "errors": str(error)}), 500
        finally:
            if conn is not None:
                cur.close()
                conn.close()

    return decorated_function


@app.route('/dbproj/admin', methods=['POST'])
@jwt_required()
@admin_required
def create_admin():
    data = flask.request.get_json()
    number_cards = data.get('number_cards')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password').encode("utf-8")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Create the user entry
        insert_user = """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING user_id;
        """
        cur.execute(insert_user, (username, email, hashed_password.decode("utf-8")))
        user_id = cur.fetchone()[0]

        # Create the admin entry
        insert_admin = """
            INSERT INTO administrator (number_cards, users_user_id)
            VALUES (%s, %s);
        """
        cur.execute(insert_admin, (number_cards, user_id))

        conn.commit()

        return flask.jsonify({"status": 200, "results": user_id})

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})

    finally:
        cur.close()
        conn.close()


@app.route('/dbproj/artist', methods=['POST'])
@jwt_required()
@admin_required
def create_artist():
    data = flask.request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password').encode("utf-8")
    name = data.get('name')
    admin_user_userid = get_jwt_identity()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    try:
        conn = db_connection()
        cur = conn.cursor()

        # Create a new user
        insert_user = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING user_id;"
        cur.execute(insert_user, (username, email, hashed_password.decode("utf-8")))
        user_id = cur.fetchone()[0]

        # Create a new artist
        insert_artist = "INSERT INTO artist (name, users_user_id, administrator_users_user_id) VALUES (%s,%s,%s);"
        cur.execute(insert_artist, (name, user_id, admin_user_userid))

        conn.commit()
        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": user_id})

    except Exception as e:
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


def artist_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        conn = db_connection()
        cur = conn.cursor()

        # Check if the user_id exists in the artist table
        check_artist = "SELECT users_user_id FROM artist WHERE users_user_id=%s;"
        cur.execute(check_artist, (user_id,))
        artist = cur.fetchone()

        cur.close()
        conn.close()

        if not artist:
            return flask.jsonify({"status": 403, "errors": "Only artists can perform this action"}), 403

        return fn(*args, **kwargs)

    return wrapper


@app.route('/dbproj/login', methods=['PUT'])
def login():
    data = flask.request.get_json()
    username = data.get('username')
    password = data.get('password').encode('utf-8')

    try:
        conn = db_connection()
        cur = conn.cursor()

        # Fetch the hashed password and user_id of the user with the given username
        query = "SELECT user_id, password FROM users WHERE username=%s;"
        cur.execute(query, (username,))
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not result or not bcrypt.checkpw(password, result[1].encode('utf-8')):  # compare with the hashed password
            return flask.jsonify({"status": 401, "errors": "Invalid username or password"})

        # Create the access token with the user_id as the identity
        user_id = result[0]  # get the user_id from the result
        access_token = create_access_token(identity=user_id)

        return flask.jsonify({"status": 200, "results": access_token})

    except Exception as e:
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


@app.route('/dbproj/card', methods=['POST'])
@jwt_required()
@admin_required
def generate_pre_paid_card():
    data = flask.request.get_json()
    number_cards = data.get('number_cards')
    card_price = data.get('card_price')
    admin_user_userid = get_jwt_identity()

    data_atual = datetime.date.today()
    limit_date = data_atual + relativedelta(months=6)

    try:
        conn = db_connection()
        cur = conn.cursor()

        if card_price == "10" or card_price == "25" or card_price == "50":
            card_price = int(card_price)
            # Create the pre_paid_card entry
            insert_pre_paid_card = """INSERT INTO pre_paid_card (card_id, card_price, limit_date, administrator_users_user_id) VALUES (%s, %s, %s, %s);"""
            card_ids = []

            for _ in range(int(number_cards)):
                card_id = ''.join(random.choices('0123456789', k=16))
                # Check if the card_id exists in the database
                cur.execute("SELECT * FROM pre_paid_card WHERE card_id = %s", (card_id,))
                result = cur.fetchone()

                while result is not None:
                    card_id = ''.join(random.choices('0123456789', k=16))
                    cur.execute("SELECT * FROM pre_paid_card WHERE card_id = %s", (card_id,))
                    result = cur.fetchone()

                cur.execute(insert_pre_paid_card, (card_id, card_price, limit_date, admin_user_userid))
                conn.commit()
                card_ids.append(card_id)


            cur.execute("SELECT * FROM administrator WHERE users_user_id = %s", (admin_user_userid,))
            result = cur.fetchone()
            new_number_cards = int(result[0])
            new_number_cards = new_number_cards + int(number_cards)
            cur.execute("UPDATE administrator SET number_cards = %s WHERE users_user_id = %s", (new_number_cards, admin_user_userid))
            conn.commit()

            cur.close()
            conn.close()
            return flask.jsonify({"status": 200, "results": card_ids})
        else:
            cur.close()
            conn.close()
            return flask.jsonify({"status": 400, "errors": "Invalid value for card_price!"})

    except Exception as e:
        cur.close()
        conn.close()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


@app.route('/dbproj/subscription', methods=['POST'])
@jwt_required()
def subscribe_to_premium():
    data = flask.request.get_json()
    address = data.get('address')
    subscription = True  # indicates user is subscribed
    telephone = data.get('telephone')
    period = data.get('period')
    cards = data.get('cards')
    user_userid = get_jwt_identity()

    try:
        conn = db_connection()
        cur = conn.cursor()

        # Check if the user exists in the consumer table/if not adds him/ this table only has data about the consumers that are or were subscribed
        cur.execute("SELECT * FROM consumer WHERE users_user_id = %s", (user_userid,))
        result = cur.fetchone()

        if result is None:
            # Inser more users information and update subscription
            update_users_data = """UPDATE consumer SET address = %s, subscription = %s, telephone = %s WHERE users_user_id = %s VALUES (address, subscription, telephone, user_userid);"""

            # Check if the value of 'period' is valid
            if period == "month" or period == "quarter" or period == "semester":
                cur.execute(update_users_data, (address, subscription, telephone, user_userid))
                subscription_id = premium_table(conn, cur, address, subscription, telephone, period, cards, user_userid)
                if subscription_id[0] is False:
                    cur.close()
                    conn.close()
                    return flask.jsonify({"status": 400, "errors": subscription_id[1]})

                conn.commit()

                cur.close()
                conn.close()
                return flask.jsonify({"status": 200, "results": subscription_id[1]})

            else:
                cur.close()
                conn.close()
                return flask.jsonify({"status": 400, "errors": "Invalid value for 'period'."})

        else:
            cur.execute("SELECT subscription FROM consumer WHERE users_user_id = %s", (user_userid,))
            result = cur.fetchone()
            get_subscription = result[0]  # Gets the value of the subscription column

            if get_subscription == True:
                #verifies if subscriptionis still on date
                get_subscription = valid_subscription(conn, cur, user_userid)

            if get_subscription != True:
                # Check if the value of 'period' is valid
                if period == "month" or period == "quarter" or period == "semester":
                    cur.execute("UPDATE consumer SET address = %s, subscription = %s, telephone = %s WHERE users_user_id = %s",(address, subscription, telephone, user_userid))
                    subscription_id = premium_table(conn, cur, address, subscription, telephone, period, cards, user_userid)
                    if subscription_id[0] is False:
                        cur.close()
                        conn.close()
                        return flask.jsonify({"status": 400, "errors": subscription_id[1]})

                    conn.commit()

                    cur.close()
                    conn.close()
                    return flask.jsonify({"status": 200, "results": subscription_id[1]})

                else:
                    cur.close()
                    conn.close()
                    return flask.jsonify({"status": 400, "errors": "Invalid value for 'period'."})

            else:
                cur.close()
                conn.close()
                return flask.jsonify({"status": 200, "results": "User already subscribed."})

    except Exception as e:
        cur.close()
        conn.close()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


#Function used in subsribe_to_premium
def premium_table(conn, cur, address, subscription, telephone, period, cards, user_userid):

    data_atual = datetime.date.today()

    if period == 'month':
        price = 7
        deadline = data_atual + relativedelta(months=1)

    elif period == 'quarter':
        price = 21
        deadline = data_atual + relativedelta(months=3)

    else:
        # if period == 'semester'
        price = 42
        deadline = data_atual + relativedelta(months=6)

    value_in_cards = 0
    #Cards verifications
    for i in range(len(cards)):
        cur.execute("SELECT premium_subscription_id FROM pre_paid_card_premium WHERE pre_paid_card_card_id = %s", (cards[i],))
        result = cur.fetchone()
        if result is not None:
            cur.execute("SELECT consumer_users_user_id FROM premium WHERE subscription_id = %s", (result,))
            result = cur.fetchone()

            if result[0] != user_userid:
                return False, ("The card %s is already associated to another user!" % cards[i])

        cur.execute("SELECT card_price, limit_date FROM pre_paid_card WHERE card_id = %s", (cards[i],))
        result = cur.fetchone()
        if result is not None:
            card_price = result[0]
            limit_date = result[1]

            if data_atual <= limit_date:
                value_in_cards = value_in_cards + card_price

            else:
                return False, ("The pre_paid_card %s is expired!" % cards[i])

        else:
            return False, ("The pre_paid_card %s is not valid!" % cards[i])

    if value_in_cards <= price:
        return False, ("The value in the cards is not enough to subscribe a %s!" % period)


    insert_subscription = "INSERT INTO premium (period, end_date, price, consumer_users_user_id) VALUES (%s, %s, %s, %s) RETURNING subscription_id;"
    cur.execute(insert_subscription, (period, deadline, price, user_userid))
    subscription_id = cur.fetchone()[0]
    value = price
    for i in range(len(cards)):
        cur.execute("SELECT card_price FROM pre_paid_card WHERE card_id = %s", (cards[i],))
        result = cur.fetchone()
        card_price = result[0]

        if value > 0:
            value = value - card_price
            card_price = card_price - price
            price = value

        if card_price <= 0:
            cur.execute("UPDATE pre_paid_card SET card_price = %s WHERE card_id = %s", (0, cards[i]))

        else:
            cur.execute("UPDATE pre_paid_card SET card_price = %s WHERE card_id = %s", (card_price, cards[i]))

        insert_pre_paid_card_premium = "INSERT INTO pre_paid_card_premium (pre_paid_card_card_id, premium_subscription_id) VALUES (%s, %s)"
        cur.execute(insert_pre_paid_card_premium, (cards[i], subscription_id))

    return True, subscription_id

#Verifies if the subscription is still on date -> this function is used everytime a user makes a premium operation
def valid_subscription(conn, cur, user_userid):

    data_atual = datetime.date.today()

    cur.execute("SELECT end_date FROM premium WHERE consumer_users_user_id = %s ORDER BY end_date DESC LIMIT 1", (user_userid,))
    last_date = cur.fetchone()

    if data_atual <= last_date[0]:
        return True
    else:
        cur.execute("UPDATE consumer SET subscription = %s WHERE users_user_id = %s",(False, user_userid))
        return False


@app.route('/dbproj/artist_info/<int:artist_id>', methods=['GET'])
@jwt_required()
def Detail_artist(artist_id):

    try:
        conn = db_connection()
        cur = conn.cursor()

        public_playlist = "public"
        # name, songs, albuns, playlists in one single querry
        artist_info = """
        SELECT t1.name, 
            (SELECT ARRAY(SELECT DISTINCT song_ismn FROM artist_song WHERE artist_users_user_id = t1.users_user_id)) AS songs,
            (SELECT ARRAY(SELECT DISTINCT album_album_id FROM artist_album WHERE artist_users_user_id = t1.users_user_id)) AS albums,
            (SELECT ARRAY(SELECT DISTINCT playlist_playlist_id FROM song_playlist INNER JOIN artist_song ON artist_song.song_ismn = song_playlist.song_ismn INNER JOIN playlist ON playlist_id = song_playlist.playlist_playlist_id WHERE artist_song.artist_users_user_id = t1.users_user_id AND playlist.visibility = %s)) AS playlists
        FROM artist t1
        WHERE t1.users_user_id = %s
        """

        cur.execute(artist_info, (public_playlist, artist_id))

        results = cur.fetchall()
        cur.close()
        conn.close()

        artist_data = {"name": results[0][0], "songs": [row[1] for row in results if row[1] is not None], "albums": [row[2] for row in results if row[2] is not None], "playlists": [row[3] for row in results if row[3] is not None]}

        if results:
            response = {"status": 200, "results": artist_data}
            return json.dumps(response, sort_keys=False)
        else:
            return flask.jsonify({"status": 400, "errors": f"Artist with ID {artist_id} does not exist!"})

    except Exception as e:
        cur.close()
        conn.close()
        traceback.print_exc()
        return False, str

    finally:
        cur.close()
        conn.close()


@app.route('/dbproj/song', methods=['POST'])
@jwt_required()
@artist_required
def add_song():
    data = flask.request.get_json()
    song_name = data.get('song_name')
    release_date = data.get('release_date')
    genre = data.get('genre')
    publisher = data.get('publisher')
    other_artists = data.get('other_artists')

    ismn = create_song(song_name, release_date, genre, publisher, other_artists)

    if ismn[0] is False:
        return flask.jsonify({"status": 400, "errors": ismn[1]})
    elif ismn[0] is True:
        return flask.jsonify({"status": 500, "errors": ismn[1]})

    return flask.jsonify({"status": 200, "results": ismn[1]})


# Songs Functions:
def create_song(song_name, release_date, genre, publisher, other_artists):
    conn = db_connection()
    cur = conn.cursor()
    user_userid = get_jwt_identity()

    genres = ["Rock", "Pop", "Hip Hop", "Jazz", "Country", "Electronic", "R&B", "Reggae", "Classical", "Folk"]
    if genre not in genres:
        return False, "Genre data is not valid!"

    try:

        # Verifies if record_label exists in the database, if not, then add
        cur.execute("SELECT * FROM record_label WHERE name = %s", (publisher,))
        result = cur.fetchone()
        if result is None:
            insert_record_label = """INSERT INTO record_label (name) VALUES (%s) """
            cur.execute(insert_record_label, (publisher,))

        insert_song = """INSERT INTO song (name, genre, release_date, duration, record_label_name, artist_users_user_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING ismn"""

        duration = random.randint(2, 7)  # Random song duration between 2 and 7 minutes

        cur.execute(insert_song, (song_name, genre, release_date, duration, publisher, user_userid))
        ismn = cur.fetchone()[0]

        insert_song_artist = """INSERT INTO artist_song (artist_users_user_id, song_ismn) VALUES (%s, %s) """
        cur.execute(insert_song_artist, (user_userid, ismn))   # Inserts main artist

        # Nome do artista que publica
        cur.execute("SELECT name FROM artist WHERE users_user_id = %s", (user_userid,))
        artist_name = cur.fetchone()

        if other_artists is not None:
            for i in range(len(other_artists)):
                if artist_name[0] == other_artists[i]:
                    cur.close()
                    conn.close()
                    return False, "The artist who published the music can not be a secundarie artist!"

                cur.execute("SELECT users_user_id FROM artist WHERE name = %s", (other_artists[i],))
                other_artist_id = cur.fetchone()
                if other_artist_id is None:
                    cur.close()
                    conn.close()
                    return False, "One of the artists associated does not exist in our database!"
                else:
                    cur.execute(insert_song_artist, (other_artist_id, ismn))  # Inserts other artist

        #In this table, we have the artist and every record_label they work with in their own songs
        #Verification if they already workerd together
        cur.execute("SELECT * FROM artist_record_label WHERE record_label_name = %s AND artist_users_user_id = %s    ", (publisher, user_userid))
        result = cur.fetchone()
        if result is None:
            insert_artist_record_label = """INSERT INTO artist_record_label (artist_users_user_id, record_label_name) VALUES (%s, %s) """
            cur.execute(insert_artist_record_label, (user_userid, publisher))

        conn.commit()

        cur.close()
        conn.close()
        return 2, ismn

    except Exception as e:
        cur.close()
        conn.close()
        traceback.print_exc()
        return True, str(e)


@app.route('/dbproj/playlist', methods=['POST'])
@jwt_required()
def Create_playlist():
    data = flask.request.get_json()
    playlist_name = data.get('playlist_name')
    visibility = data.get('visibility')
    songs = data.get('songs')
    user_userid = get_jwt_identity()

    try:
        conn = db_connection()
        cur = conn.cursor()

        subscription = valid_subscription(conn, cur, user_userid)

        if subscription is True:
            insert_playlist = """INSERT INTO playlist (playlist_name, visibility, consumer_users_user_id) VALUES (%s, %s, %s) RETURNING playlist_id"""
            cur.execute(insert_playlist, (playlist_name, visibility, user_userid))
            playlist_id = cur.fetchone()[0]

            insert_song_playlist = """INSERT INTO song_playlist (song_ismn, playlist_playlist_id) VALUES (%s, %s) """

            if songs is not None:
                for i in range(len(songs)):
                    cur.execute(insert_song_playlist, (songs[i], playlist_id))  # Inserts main artist

                conn.commit()
                cur.close()
                conn.close()
                return flask.jsonify({"status": 200, "results": playlist_id})

            else:
                cur.close()
                conn.close()
                return flask.jsonify({"status": 400, "errors": "To create a playlist you need at least one song!"})

        else:
            return flask.jsonify({"status": 400, "errors": "You don´t have permission to create a playlist. Subscribe to premium if you want to create playlists."})

    except Exception as e:
        cur.close()
        conn.close()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})



@app.route('/dbproj/album', methods=['POST'])
@jwt_required()
@artist_required
def add_album():
    data = flask.request.get_json()
    album_name = data.get('name')
    release_date = data.get('release_date')
    publisher = data.get('publisher')
    songs = data.get('songs')
    user_userid = get_jwt_identity()

    conn = db_connection()
    cur = conn.cursor()

    try:

        # Verifies if record_label exists in the database, if not, then add
        cur.execute("SELECT * FROM record_label WHERE name = %s", (publisher,))
        result = cur.fetchone()
        if result is None:
            insert_record_label = """INSERT INTO record_label (name) VALUES (%s) """
            cur.execute(insert_record_label, (publisher,))

        cur.execute("""SELECT name FROM artist WHERE users_user_id = %s""", (user_userid,))
        artist_name = cur.fetchone()

        # Create the album entry
        insert_album = """INSERT INTO album (album_name, release_date, record_label_name) VALUES (%s, %s, %s) RETURNING album_id """
        cur.execute(insert_album, (album_name, release_date, publisher))
        album_id = cur.fetchone()[0]

        # Associate the album with the songs
        associate_song = """INSERT INTO album_song (song_ismn, album_album_id) VALUES (%s, %s);"""
        for song in songs:
            if type(song) == dict:
                # If song is a dictionary, we assume it's a new song to be added
                song_ismn = create_song(song['song_name'], song['release_date'], song['genre'],song['publisher'], song['other_artists'])
                if song_ismn[0] != 2:
                    cur.close()
                    conn.close()
                    return flask.jsonify({"status": 400, "errors": song_ismn[1]})
                song_ismn = song_ismn[1]

            else:
                # If song is not a dictionary, we assume it's an existing song
                song_ismn = song

                # Validate if the artist is associated with the selected existing song
                cur.execute("""SELECT * FROM song WHERE artist_users_user_id = (SELECT users_user_id FROM artist WHERE name = %s) AND ismn = %s""", (artist_name, song_ismn))
                result = cur.fetchone()
                if result is None:
                    cur.close()
                    conn.close()
                    return flask.jsonify({"status": 400, "errors": "Artist not associated with song"})

            cur.execute(associate_song, (song_ismn, album_id))

        insert_artist_album =  """INSERT INTO artist_album (artist_users_user_id, album_album_id) VALUES (%s, %s);"""
        cur.execute(insert_artist_album, (user_userid, album_id))

        # In this table, we have the artist and every record_label they work with in their own songs
        # Verification if they already workerd together
        cur.execute("SELECT * FROM artist_record_label WHERE record_label_name = %s AND artist_users_user_id = %s    ",(publisher, user_userid))
        result = cur.fetchone()
        if result is None:
            insert_artist_record_label = """INSERT INTO artist_record_label (artist_users_user_id, record_label_name) VALUES (%s, %s) """
            cur.execute(insert_artist_record_label, (user_userid, publisher))

        conn.commit()
        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": album_id})

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})



@app.route('/dbproj/<int:song_id>', methods=['PUT'])
@jwt_required()  # protect this route with JWT
def play_song(song_id):
    # Get the user's id from the JWT token
    user_id = get_jwt_identity()

    # Connect to the database
    db = db_connection()
    cur = db.cursor()

    # Generate a random id for the stream
    id_stream = generate_unique_id(cur)

    # Get the current timestamp
    stream_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Try to insert a new row into the stream table
    try:
        cur.execute(
            "INSERT INTO stream (id_stream, stream_date, song_ismn, consumer_users_user_id) VALUES (%s, %s, %s, %s)",
            (id_stream, stream_date, song_id, user_id)
        )

        # Commit the transaction
        db.commit()

        return flask.jsonify({"status": 200})

    except psycopg2.Error as e:
        # If an error occurs, roll back the transaction
        db.rollback()

        # Log the error and return a 500 status code
        return flask.jsonify({"status": 500, "errors": str(e)})


def generate_unique_id(cur):
    id_stream =random.randint(1, int(1e9))

    cur.execute("SELECT id_stream FROM stream WHERE id_stream = %s", (id_stream,))
    result = cur.fetchone()

    while result is not None:
        id_stream = random.randint(1, int(1e9))
        cur.execute("SELECT id_stream FROM stream WHERE id_stream = %s", (id_stream,))
        result = cur.fetchone()

    return id_stream


@app.route('/dbproj/song/<string:keyword>', methods=['GET'])
@jwt_required()
def search_song(keyword):
    # Connect to the database
    db = db_connection()
    cur = db.cursor()

    # Try to fetch data using the SQL query
    try:
        cur.execute(
            """
            SELECT song.ismn AS song_ismn, song.name AS song_title, artist.name AS artist_name, album.album_id AS album_id 
            FROM song 
            LEFT JOIN artist_song ON song.ismn = artist_song.song_ismn
            LEFT JOIN artist ON artist_song.artist_users_user_id = artist.users_user_id
            LEFT JOIN album_song ON song.ismn = album_song.song_ismn
            LEFT JOIN album ON album_song.album_album_id = album.album_id
            WHERE song.name LIKE %s
            """,
            ('%' + keyword + '%',)  # The '%' before and after the keyword means that the keyword can be at any position in the song title
        )
        results = cur.fetchall()

        # Process the results
        response = {"status": 200, "results": []}
        song_dict = {}
        for result in results:
            song_ismn, song_title, artist_name, album_id = result
            if song_ismn not in song_dict:
                song_dict[song_ismn] = {"title": song_title, "artists": [], "albums": []}
            if artist_name not in song_dict[song_ismn]["artists"]:
                song_dict[song_ismn]["artists"].append(artist_name)
            if album_id not in song_dict[song_ismn]["albums"]:
                song_dict[song_ismn]["albums"].append(album_id)

        # Convert song_dict to list of song dictionaries
        response["results"] = list(song_dict.values())

        return flask.jsonify(response)

    except psycopg2.Error as e:
        # If an error occurs, roll back the transaction
        db.rollback()

        # Log the error and return a 500 status code
        return flask.jsonify({"status": 500, "errors": str(e)})


@app.route('/dbproj/comments/<int:song_id>', methods=['POST'])
@jwt_required()
def leave_comment(song_id):
    data = flask.request.get_json()
    comment = data.get('comment')
    user_id = get_jwt_identity()

    # Connect to the database
    conn = db_connection()
    cur = conn.cursor()

    try:

        insert_comment = "INSERT INTO coment (texto, consumer_users_user_id) VALUES (%s, %s) RETURNING comment_id"
        cur.execute(insert_comment, (comment, user_id))
        comment_id = cur.fetchone()[0]

        insert_comment_song = "INSERT INTO coment_song (coment_comment_id, song_ismn) VALUES (%s, %s)"
        cur.execute(insert_comment_song, (comment_id, song_id))

        conn.commit()
        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": comment_id})

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


@app.route('/dbproj/comments/<int:song_id>/<int:parent_comment_id>', methods=['POST'])
@jwt_required()
def leave_comment_reply(song_id, parent_comment_id):
    data = flask.request.get_json()
    comment = data.get('comment')
    user_id = get_jwt_identity()

    # Connect to the database
    conn = db_connection()
    cur = conn.cursor()

    try:

        insert_comment = "INSERT INTO coment (texto, consumer_users_user_id) VALUES (%s, %s) RETURNING comment_id"
        cur.execute(insert_comment, (comment, user_id))
        comment_id = cur.fetchone()[0]

        insert_comment_song = "INSERT INTO coment_song (coment_comment_id, song_ismn) VALUES (%s, %s)"
        cur.execute(insert_comment_song, (comment_id, song_id))

        insert_comment_reply = "INSERT INTO coment_coment (coment_comment_id, coment_comment_id1) VALUES (%s, %s)"
        cur.execute(insert_comment_reply, (comment_id, parent_comment_id))

        conn.commit()
        cur.close()
        conn.close()

        return flask.jsonify({"status": 200, "results": comment_id})

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return flask.jsonify({"status": 500, "errors": str(e)})


if __name__ == '__main__':
    app.run(debug=True)