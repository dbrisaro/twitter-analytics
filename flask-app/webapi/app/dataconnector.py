import sqlite3
import json
from app import app, datautil

def get_users():
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = 'SELECT * FROM users' 
    cursor.execute(statement)

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_user(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = 'SELECT * FROM users WHERE screen_name COLLATE NOCASE = ? LIMIT 1' 
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_tweets(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = 'SELECT * FROM tweets WHERE author_id = (SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?) AND text NOT LIKE "RT @%"' 
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_snapshots(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = 'SELECT * FROM user_snapshots WHERE user_id = (SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?)' 
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_retweet_volume(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = f"""SELECT sum(retweets) retweets, case cast (strftime('%w', local_time) as integer)
                    when 0 then 'Sunday'
                    when 1 then 'Monday'
                    when 2 then 'Tuesday'
                    when 3 then 'Wednesday'
                    when 4 then 'Thursday'
                    when 5 then 'Friday'
                    else 'Saturday' end as day_of_week, strftime('%H:00', local_time) tweet_hour FROM (
                        SELECT time_of_tweet, retweets, datetime(time_of_tweet, 'localtime') local_time FROM tweets 
                        WHERE author_id= (SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?)
                            AND text NOT LIKE 'RT @%'
                        ORDER BY retweets DESC)
                    GROUP BY day_of_week, tweet_hour"""
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_like_volume(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = f"""SELECT sum(likes) likes, case cast (strftime('%w', local_time) as integer)
                    when 0 then 'Sunday'
                    when 1 then 'Monday'
                    when 2 then 'Tuesday'
                    when 3 then 'Wednesday'
                    when 4 then 'Thursday'
                    when 5 then 'Friday'
                    else 'Saturday' end as day_of_week, strftime('%H:00', local_time) tweet_hour FROM (
                        SELECT time_of_tweet, likes, datetime(time_of_tweet, 'localtime') local_time FROM tweets 
                        WHERE author_id= (SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?)
                            AND text NOT LIKE 'RT @%'
                        ORDER BY likes DESC)
                    GROUP BY day_of_week, tweet_hour"""
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_tweet_volume(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = f"""SELECT count(*) total_tweets, case cast (strftime('%w', local_time) as integer)
                    when 0 then 'Sunday'
                    when 1 then 'Monday'
                    when 2 then 'Tuesday'
                    when 3 then 'Wednesday'
                    when 4 then 'Thursday'
                    when 5 then 'Friday'
                    else 'Saturday' end as day_of_week, strftime('%H:00', local_time) tweet_hour FROM (
                        SELECT time_of_tweet, datetime(time_of_tweet, 'localtime') local_time FROM tweets 
                        WHERE author_id=(SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?)
                            AND text NOT LIKE 'RT @%'
                        ORDER BY time_of_tweet DESC)
                    GROUP BY day_of_week, tweet_hour"""
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_monthly_tweets(name):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = f"""SELECT count(*) total_tweets, strftime("%m-%Y", time_of_tweet) aggregatedate  FROM (
                        SELECT time_of_tweet FROM tweets 
                        WHERE author_id=(SELECT id FROM users WHERE screen_name COLLATE NOCASE = ?)
                            AND text NOT LIKE 'RT @%'
                        ORDER BY time_of_tweet DESC)
                    GROUP BY aggregatedate"""
    cursor.execute(statement, (name,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)

def get_tweet_snapshots(id):
    data_connection = sqlite3.connect(app.config['DATASTORE_PATH'])
    data_connection.row_factory = sqlite3.Row

    cursor = data_connection.cursor()

    statement = f"""SELECT * FROM tweet_snapshots 
                        WHERE id= ? 
                        ORDER BY time_of_capture ASC"""
    cursor.execute(statement, (id,))

    data = cursor.fetchall()

    return datautil.get_named_entities(data)