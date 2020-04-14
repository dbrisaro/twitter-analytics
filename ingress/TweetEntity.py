class TweetEntity(object):
    def __init__(self, created_date, tweet_id, likes, retweets):
        self.creatred_date = created_date
        self.tweet_id = tweet_id
        self.likes = likes
        self.retweets = retweets