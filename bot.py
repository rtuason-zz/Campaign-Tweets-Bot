from os import makedirs
from os.path import exists
from os.path import join
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import argparse

import csv
import json
import requests
import re
import calendar
from dateutil import parser as dateparser

import boto3
from twython import Twython

SRC_URL = 'http://stash.compciv.org/2017/kaggletrumptweets.zip'
DATA_DIR = 'data'
RAW_FILENAME = 'campaign_tweets.csv'

MIN_DATE = '4/17/16'
MAX_DATE = '9/29/16'  # Include tweets through 9/28/16 11:59pm

######################################################################
# General tweet functions
######################################################################
def fetch_tweets(filename):
  if not exists(filename):
    url = urlopen(SRC_URL)
    zipfile = ZipFile(BytesIO(url.read()))
    zipfile.extractall(DATA_DIR)

def read_tweets():
  makedirs(DATA_DIR, exist_ok=True)
  filename = join(DATA_DIR, RAW_FILENAME)

  fetch_tweets(filename)
  with open(filename, 'r') as f:
    tweets = list(csv.DictReader(f))
    return tweets

def get_tweet_stats(tweets):
  retweet_sum = 0
  favorite_sum = 0

  for tweet in tweets:
    retweet_sum += int(tweet['retweet_count'])
    favorite_sum += int(tweet['favorite_count'])

  retweet_avg = "{:,.2f}".format(round(retweet_sum / len(tweets), 2))
  favorite_avg = "{:,.2f}".format(round(favorite_sum / len(tweets), 2))
  num_tweets = format(len(tweets), ',d')

  return num_tweets, retweet_avg, favorite_avg

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
  output = "From {date1} to {date2}, Hillary Clinton's {HC_num_tweets} tweets averaged {HC_retweet_avg} retweets and {HC_favorite_avg} favorites, while Donald Trump's {DT_num_tweets} tweets averaged {DT_retweet_avg} retweets and {DT_favorite_avg} favorites."
  output = output.format(
    date1=date1.strftime("%b %d, %Y"),
    date2=date2.strftime("%b %d, %Y"),
    HC_num_tweets=clinton_stats[0],
    HC_retweet_avg=clinton_stats[1],
    HC_favorite_avg=clinton_stats[2],
    DT_num_tweets=trump_stats[0],
    DT_retweet_avg=trump_stats[1],
    DT_favorite_avg=trump_stats[2]
  )

  return output

# The normal response is longer than 140 characters, so split it into 
# two responses that the Twitter API will accept. 
def create_twitter_response(date1, date2, clinton_stats, trump_stats):
  output1 = "From {date1} to {date2}, Hillary Clinton's {HC_num_tweets} tweets averaged {HC_retweet_avg} retweets and {HC_favorite_avg} favorites, while..."
  output2 = "Donald Trump's {DT_num_tweets} tweets averaged {DT_retweet_avg} retweets and {DT_favorite_avg} favorites."
  
  output1 = output1.format(
    date1=date1.strftime("%b %d, %Y"),
    date2=date2.strftime("%b %d, %Y"),
    HC_num_tweets=clinton_stats[0],
    HC_retweet_avg=clinton_stats[1],
    HC_favorite_avg=clinton_stats[2]
  )
  output2 = output2.format(
    DT_num_tweets=trump_stats[0],
    DT_retweet_avg=trump_stats[1],
    DT_favorite_avg=trump_stats[2]
  )

  return output1, output2

######################################################################
# Send response as texts or tweets, if applicable
######################################################################
def send_texts(args, response):
  if args.phone:
    phone_pattern = re.compile("^\+1\d{10}$")
    for phone_number in args.phone:
      if not phone_pattern.match(phone_number):
        print("At least one phone number has been formatted incorrectly. Phone numbers must start with '+1', followed by ten numbers.")
        return   # Don't exit program. There might be Twitter handles.

    session = boto3.Session(profile_name='default')
    sns = session.client('sns')
    for phone_number in args.phone:
      sns.publish(PhoneNumber='+1' + phone_number, Message=response)

def send_tweets(args, date1, date2, clinton_stats, trump_stats):
  if args.twitter:
    twitter_pattern = re.compile("^[\w]{1,15}$")
    for handle in args.twitter:
      if not twitter_pattern.match(handle):
        print("At least one Twitter handle has been formatted incorrectly.")
        return

    with open('twitter-creds.json') as f:
      creds = json.load(f)

    client = Twython(creds['consumer_key'], creds['consumer_secret'], creds['access_token'], creds['access_token_secret'])

    response1, response2 = create_twitter_response(date1, date2, clinton_stats, trump_stats)

    for handle in args.twitter:
      msg1 = "@{} {}".format(handle, response1)
      msg2 = "@{} {}".format(handle, response2)
      client.update_status(status=msg1)
      client.update_status(status=msg2)

######################################################################
# Analyze user input arguments and provide tweet stats pertaining to 
# a range of dates to given output channels
######################################################################
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--dates", nargs="*")
  parser.add_argument("--phone", nargs="*")
  parser.add_argument("--twitter", nargs="*")
  args = parser.parse_args()

  min_date = dateparser.parse(MIN_DATE)
  max_date = dateparser.parse(MAX_DATE)

  if args.dates:
    date_pattern = re.compile("^[4-9]/\d{1,2}/16$")
    
    if len(args.dates) == 2 and date_pattern.match(args.dates[0]) and date_pattern.match(args.dates[1]):
      try:
        temp1 = dateparser.parse(args.dates[0])
        temp2 = dateparser.parse(args.dates[1])
      except:
        print("Invalid date(s) provided. They must also follow the format m/dd/yy.")
        exit()

      date1 = min(temp1, temp2)   # Make sure that date1 is always
      date2 = max(temp1, temp2)   # before or the same date as date2

      if date1 >= min_date and date2 <= max_date:
        clinton_stats, trump_stats = compare_tweets(date1, date2)
        response = create_response(date1, date2, clinton_stats, trump_stats)
      else:
        print("Your date range must fall between 4/17/16 and 9/29/16, inclusive")
        exit()
    else:
      print("If using dates, you must provide exactly two that follow the format 'm/dd/yy'.")
      exit()
  else:
    clinton_stats, trump_stats = compare_tweets(min_date, max_date)
    date1, date2 = min_date, max_date
    response = create_response(date1, date2, clinton_stats, trump_stats)

  print(response)

  send_texts(args, response)
  send_tweets(args, date1, date2, clinton_stats, trump_stats)  