import twitter
from datetime import datetime
import time

def start_ingress(service, account, config, data_connection):
    if service.lower() == 'twitter':
        twitter_api = get_twitter_instance(config)

        while True:
            try:
                user = twitter_api.GetUser(screen_name=account)

                if not user_exists(user, data_connection):
                    capture_user(user, data_connection)
                
                take_user_snapshot(user, data_connection)

                update_user_tweets(user.screen_name, config, data_connection)
            except twitter.error.TwitterError as rate_error:
                print(f"[error] Hit a rate limit error. {rate_error.message}. Sleeping started at {datetime.now()}...")
                time.sleep(900)
            break

def get_replies(user, tweet_id, config):
    print(f'[info] Attempting to get replies for tweet {tweet_id}...')
    twitter_api = get_twitter_instance(config)

    # Ensure that the whole thing is encoded.
    query = f'q=%28to%3A{user}%29%20since_id%3A{tweet_id}'

    while True:
        try:
            results = twitter_api.GetSearch(raw_query=query, count=100)

            reply_results = []

            for result in results:
                if str(result.in_reply_to_status_id) == tweet_id:
                    reply_results.append(result)

            return len(reply_results)
        except twitter.error.TwitterError as rate_error:
            print(f"[error] Hit a rate limit error. {rate_error.message}. Sleeping started at {datetime.now()}...")
            time.sleep(900)
        break

def get_twitter_instance(config):
    return twitter.Api(consumer_key=config['Twitter']['ConsumerKey'],
                                  consumer_secret=config['Twitter']['ConsumerSecret'],
                                  access_token_key=config['Twitter']['AccessToken'],
                                  access_token_secret=config['Twitter']['AccessTokenSecret'],
                                  tweet_mode='extended',
                                  sleep_on_rate_limit=True)

def tweet_exists(tweet_id, data_connection):
    cursor = data_connection.cursor()
    cursor.execute(f'SELECT 1 FROM tweets WHERE id={tweet_id} LIMIT 1')
    return  cursor.fetchone() is not None

def log_tweet(tweet, config, data_connection):
    cursor = data_connection.cursor()
    current_time = get_current_time_to_schema_date()

    tweet_has_media = tweet.media is not None
    tweet_is_quote_retweet = tweet.quoted_status is not None

    tweet_is_reply = int(tweet.in_reply_to_status_id is not None)
    tweet_reply_to_user = tweet.in_reply_to_user_id
    tweet_time = get_twitter_date_to_schema_date(tweet.created_at)

    # Need to validate that the replies are non-empty.
    tweet_replies = get_replies(tweet.user.screen_name, tweet.id_str, config)
    tweet_replies = tweet_replies if tweet_replies is not None else 0

    print(f'[info] Storing {tweet.id_str}...')

    statement = 'SELECT replies FROM tweets WHERE id = ?'

    current_replies = cursor.execute(statement, (tweet.id_str,)).fetchone()
    
    # We only want to update the number of replies if the result we get from search is
    # larger than what we already have (given the volatility of search results.)
    if current_replies is not None and len(current_replies) > 0 and current_replies[0] is not None:
        if current_replies[0] > tweet_replies:
            tweet_replies = current_replies[0]

    # Captures the tweet itself in a standalone capacity
    statement = 'INSERT OR REPLACE INTO tweets (id, likes, retweets, is_reply, reply_to_user, time_of_tweet, time_of_capture, author_id, location, replies, text, has_media, is_quote_retweet) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'   
    cursor.execute(statement, (tweet.id_str, tweet.favorite_count, tweet.retweet_count, tweet_is_reply, tweet_reply_to_user, tweet_time, current_time, tweet.user.id_str, tweet.coordinates, tweet_replies, tweet.full_text, tweet_has_media, tweet_is_quote_retweet))
    data_connection.commit()

    # Captures the tweet snapshot for further analysis
    statement = 'INSERT OR REPLACE INTO tweet_snapshots (id, retweets, likes, replies, time_of_capture) VALUES (?, ?, ?, ?, ?)'   
    cursor.execute(statement, (tweet.id_str, tweet.retweet_count, tweet.favorite_count, tweet_replies, current_time))
    data_connection.commit()

    print(f'[info] Stored {tweet.id_str}.')

def update_user_tweets(user, config, data_connection):
    print(f'[info] Preparing to aggregate tweets for user {user}...')
    twitter_api = get_twitter_instance(config)

    while True:
        try:
            timeline = twitter_api.GetUserTimeline(screen_name=user, count=200)

            for tweet in timeline:
                log_tweet(tweet, config, data_connection)

            print(f'[info] Timeline for {user} captured.')
        except twitter.error.TwitterError as rate_error:
            print(f"[error] Hit a rate limit error. {rate_error.message}. Sleeping started at {datetime.now()}...")
            time.sleep(900)
        break

def take_user_snapshot(user, data_connection):
    cursor = data_connection.cursor()

    print(f'[info] Preparing to take snapshot for user {user.id_str}...')
    
    current_time = get_current_time_to_schema_date()

    cursor.execute(f'INSERT INTO user_snapshots (follower_count, following_count, tweet_count, like_count, time_of_capture, listed_count, user_id) VALUES ("{user.followers_count}", "{user.friends_count}", "{user.statuses_count}", "{user.favourites_count}", "{current_time}", "{user.listed_count}", "{user.id_str}")')
    data_connection.commit()
    print(f'[info] Snapshot for user {user.id_str} added.')

def user_exists(user, data_connection):
    cursor = data_connection.cursor()
    statement = "SELECT * FROM users WHERE id COLLATE NOCASE = ? LIMIT 1"
    cursor.execute(statement, (user.id_str,))
    return cursor.fetchone() is not None

def capture_user(user, data_connection):
    cursor = data_connection.cursor()

    print(f'[info] User {user.id_str} does not exist in the database. Adding...')
    
    current_time = get_current_time_to_schema_date()
    converted_date = get_twitter_date_to_schema_date(user.created_at)

    cursor.execute(f'INSERT INTO users (id, name, bio, time_of_registration, time_of_capture, location, screen_name) VALUES ("{user.id_str}", "{user.name}", "{user.description}", "{converted_date}", "{current_time}", "{user.location}", "{user.screen_name}")')
    data_connection.commit()
    print(f'[info] User {user.id_str} added.')

def get_twitter_date_to_schema_date(twitter_date):
    converted_date_raw = datetime.strptime(twitter_date, "%a %b %d %H:%M:%S %z %Y")

    return converted_date_raw.isoformat()
    #return converted_date_raw.strftime("%m/%d/%Y %H:%M:%S")

def get_current_time_to_schema_date():
    current_time = datetime.now()
    
    return current_time.isoformat()
    #return current_time.strftime("%m/%d/%Y %H:%M:%S")