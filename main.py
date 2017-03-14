from os.path import exists
import argparse

import csv
import requests
import re
import calendar
from dateutil import parser as dateparser

import boto3
from twython import Twython

SRC_URL = 'https://stanford.edu/~rtuason/campaign_tweets.csv'
FILENAME = 'campaign-tweets.csv'

MIN_DATE = '4/17/16'
MAX_DATE = '9/29/16'  # Include tweets through 9/28/16 11:59pm

######################################################################
# General tweet functions
######################################################################

def fetch_tweets():
  if not exists(FILENAME):
    resp = requests.get(SRC_URL)
    with open(FILENAME, 'wb') as f:
      f.write(resp.content)

def read_tweets():
  fetch_tweets()
  with open(FILENAME, 'r') as f:
    tweets = list(csv.DictReader(f))
    return tweets

def get_tweet_stats(tweets):
  retweet_sum = 0
  favorite_sum = 0

  for tweet in tweets:
    retweet_sum += int(tweet['retweet_count'])
    favorite_sum += int(tweet['favorite_count'])

  retweet_avg = round(retweet_sum / len(tweets), 2)
  favorite_avg = round(favorite_sum / len(tweets), 2)

  return retweet_avg, favorite_avg, len(tweets)

######################################################################
# Tweet functions for a range of dates
######################################################################

def filter_tweets(tweets, handle, date1, date2):
  results = []
  for tweet in tweets:
    if tweet['handle'] == handle and tweet['is_retweet'] == 'False':
      tweet_time = dateparser.parse(tweet['time'])
      if tweet_time >= date1 and tweet_time <= date2:
        results.append(tweet)

  return results

def compare_tweets(date1, date2):
  tweets = read_tweets()

  clinton_tweets = filter_tweets(tweets, 'HillaryClinton', date1, date2)
  trump_tweets = filter_tweets(tweets, 'realDonaldTrump', date1, date2)

  clinton_stats = get_tweet_stats(clinton_tweets)
  trump_stats = get_tweet_stats(trump_tweets)

  return clinton_stats, trump_stats

######################################################################
# Formulate a response
######################################################################
def create_response(date1, date2, clinton_stats, trump_stats):
  output = "From {date1} to {date2}, Hillary Clinton had averages of {HC_retweet_avg} retweets and {HC_favorite_avg} favorites from {HC_num_tweets} tweets, while Donald Trump had averages of {DT_retweet_avg} retweets and {DT_favorite_avg} favorites from {DT_num_tweets} tweets."
  output = output.format(
    date1=date1,
    date2=date2,
    HC_retweet_avg=clinton_stats[0],
    HC_favorite_avg=clinton_stats[1],
    HC_num_tweets=clinton_stats[2],
    DT_retweet_avg=trump_stats[0],
    DT_favorite_avg=trump_stats[1],
    DT_num_tweets=trump_stats[2]
  )

  return output

######################################################################
# Analyze user input arguments
######################################################################

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--date", nargs="*")
  parser.add_argument("--phone", nargs="*")
  parser.add_argument("--twitter", nargs="*")
  args = parser.parse_args()

  min_date = dateparser.parse(MIN_DATE)
  max_date = dateparser.parse(MAX_DATE)

  if args.date:
    date_pattern = re.compile("^[4-9]/\d{1,2}/16$")
    
    if len(args.date) == 2 and date_pattern.match(args.date[1]) and date_pattern.match(args.date[2]):
      try:
        temp1 = dateparser.parse(args.date[1])
        temp2 = dateparser.parse(args.date[2])
      else:
        print("Invalid date(s) provided. They must also follow the format m/dd/yy.")
        return

      date1 = min(temp1, temp2)
      date2 = max(temp1, temp2)

      if date1 >= min_date and date2 <= max_date:
        clinton_stats, trump_stats = compare_tweets(date1, date2)
        response = create_response(date1, date2, clinton_stats, trump_stats)
      else:
        print("Your date range must fall between 4/17/16 and 9/29/16, inclusive")
        return
    else:
      print("If using dates, exactly two must be provided.")
      return
  else:
    clinton_stats, trump_stats = compare_tweets(min_date, max_date)
    response = create_response(min_date, max_date, clinton_stats, trump_stats)

  print(response + '\n')

  if args.phone:
    phone_pattern = re.compile("^\+1\d{10}$")
    numbers_correct = True
    for phone_number in args.phone:
      if not phone_pattern.match(phone_number):
        print("At least one phone number has been formatted incorrectly. Phone numbers must start with '+1', followed by ten numbers.")
        numbers_correct = False
        break

    if numbers_correct:
      session = boto3.Session(profile_name='default')
      sns = session.client('sns')
      for phone_number in args.phone:
        # sns.publish(PhoneNumber=phone_number, Message=response)

  if args.twitter:
    twitter_pattern = re.compile("^[\w]{1,15}$")
    handles_correct = True
    for handle in args.twitter:
      if not twitter_pattern.match(handle):
        print("At least one Twitter handle has been formatted incorrectly.")
        handles_correct = False
        break

    if handles_correct:
      with open('twitter-creds.json') as f:
        creds = json.load(f)

      client = Twython(creds['consumer_key'], creds['consumer_secret'], creds['access_token'], creds['access_token_secret'])
      for handle in args.twitter:
        msg = "@{} {}".format(handle, response)
        client.update_status(status=msg)