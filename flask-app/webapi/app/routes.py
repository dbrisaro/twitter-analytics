from app import app
from flask import jsonify
from flask_cors import CORS, cross_origin
from app import dataconnector

@app.route('/users')
def users():
    data = dataconnector.get_users()
    return jsonify(data)

@app.route('/users/<name>')
def user(name):
    data = dataconnector.get_user(name)
    return jsonify(data)

@app.route('/users/<name>/tweets')
@cross_origin(origin='localhost')
def tweets(name):
    data = dataconnector.get_tweets(name)
    return jsonify(data)

@app.route('/users/<name>/snapshots')
@cross_origin(origin='localhost')
def snapshots(name):
    data = dataconnector.get_snapshots(name)
    return jsonify(data)

@app.route('/users/<name>/stats/retweetvolume')
@cross_origin(origin='localhost')
def retweet_volume(name):
    data = dataconnector.get_retweet_volume(name)
    return jsonify(data)

@app.route('/users/<name>/stats/likevolume')
@cross_origin(origin='localhost')
def like_volume(name):
    data = dataconnector.get_like_volume(name)
    return jsonify(data)

@app.route('/users/<name>/stats/tweetvolume')
@cross_origin(origin='localhost')
def tweet_volume(name):
    data = dataconnector.get_tweet_volume(name)
    return jsonify(data)

@app.route('/users/<name>/stats/monthlytweets')
@cross_origin(origin='localhost')
def monthly_tweets(name):
    data = dataconnector.get_monthly_tweets(name)
    return jsonify(data)

@app.route('/tweets/<id>/snapshots')
@cross_origin(origin='localhost')
def tweet_snapshots(id):
    data = dataconnector.get_tweet_snapshots(id)
    return jsonify(data)