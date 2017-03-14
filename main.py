from os.path import exists
import argparse

import csv
import requests
import re
import calendar
from dateutil import parser as dateparser

import boto3

SRC_URL = 'https://stanford.edu/~rtuason/campaign_tweets.csv'
FILENAME = 'campaign-tweets.csv'

MIN_MONTH = 4
MAX_MONTH = 9

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
# Tweet functions for a range of months
######################################################################

def filter_tweets(tweets, handle, min_month, max_month):
  results = []
  for tweet in tweets:
    if tweet['handle'] == handle and tweet['is_retweet'] == 'False':
      tweet_time = dateparser.parse(tweet['time'])
      if tweet_time.month >= min_month and tweet_time.month <= max_month:
        results.append(tweet)

  return results

def compare_tweets(min_month, max_month):
  tweets = read_tweets()

  clinton_tweets = filter_tweets(tweets, 'HillaryClinton', min_month, max_month)
  trump_tweets = filter_tweets(tweets, 'realDonaldTrump', min_month, max_month)

  clinton_stats = get_tweet_stats(clinton_tweets)
  trump_stats = get_tweet_stats(trump_tweets)

  return clinton_stats, trump_stats

######################################################################
# Functions for formulating a response
######################################################################
def get_month_stats(month_str):
  date = dateparser.parse(argv[1])
  month_str = calendar.month_name[date.month]
  clinton_stats, trump_stats = compare_tweets(date.month)

  output = "In {month} 2016, Hillary Clinton had averages of {HC_retweet_avg} retweets and {HC_favorite_avg} favorites from {HC_num_tweets} tweets, while Donald Trump had averages of {DT_retweet_avg} retweets and {DT_favorite_avg} favorites from {DT_num_tweets} tweets."
  output = output.format(
    month=month_str,
    HC_retweet_avg=clinton_stats[0],
    HC_favorite_avg=clinton_stats[1],
    HC_num_tweets=clinton_stats[2],
    DT_retweet_avg=trump_stats[0],
    DT_favorite_avg=trump_stats[1],
    DT_num_tweets=trump_stats[2]
  )

  return output

def get_all_months_stats():
  clinton_stats, trump_stats = compare_all_tweets()

  output = "From April to September 2016, Hillary Clinton had averages of {HC_retweet_avg} retweets and {HC_favorite_avg} favorites from {HC_num_tweets} tweets, while Donald Trump had averages of {DT_retweet_avg} retweets and {DT_favorite_avg} favorites from {DT_num_tweets} tweets."
  output = output.format(
    HC_retweet_avg=clinton_stats[0],
    HC_favorite_avg=clinton_stats[1],
    HC_num_tweets=clinton_stats[2],
    DT_retweet_avg=trump_stats[0],
    DT_favorite_avg=trump_stats[1],
    DT_num_tweets=trump_stats[2]
  )

  return output
  
def print_error_message():
  print("Provide a target month to see tweet statistics about Hillary Clinton and Donald Trump. Your target month must follow the format 'yyyy-mm' and must fall between April and September of 2016, inclusive.\n")
  print("You may also provide a phone number to which you would like these statistics to be sent. If you provide a phone number but not a target month, statistics will be aggregated from April to September 2016. Your phone number must contain '+1' followed by ten numbers.\n")


######################################################################
# Analyze user input arguments
######################################################################

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--month", type=int, nargs="*")
  parser.add_argument("--phone", nargs="*")
  parser.add_argument("--email", nargs="*")
  args = parser.parse_args()

  if args.month:
    if len(args.month) == 1 and args.month[0] >= MIN_MONTH and args.month[0] <= MAX_MONTH:
      min_month = args.month[0]
      max_month = args.month[0]

    elif len(args.month) == 2 and args.month[0] >= MIN_MONTH and args.month[1] <= MAX_MONTH and args.month[0] <= args.month[1]:
      min_month = args.month[0]
      max_month = args.month[1]

    else:
      print_error_message()
      return

  else:
    min_month = MIN_MONTH
    max_month = MAX_MONTH

  if args.phone:
    phone_pattern = re.compile("^\+1\d{10}$")
    for phone_number in args.phone:
      if not phone_pattern.match(phone_number):
        print_error

    if phone_pattern.match(phone_number):
      output = get_month_stats()
      # sns.publish(PhoneNumber=phone_number, Message=output)



  # if args.hello:
  #   print(len(args.hello))

  month_pattern = re.compile("^2016\-0[4-9]$")
  email_pattern = re.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$")
  
  session = boto3.Session(profile_name='default')
  sns = session.client('sns')

  if len(argv) == 2:
    if month_pattern.match(argv[1]):
      output = get_month_stats(argv[1])
      print(output)

    elif phone_pattern.match(argv[1]):
      output = get_all_months_stats(argv[1])
      # sns.publish(PhoneNumber=argv[1], Message=output)

  elif len(argv) == 3:
    if month_pattern.match(argv[1]) and phone_pattern.match(argv[2]):
      output = get_month_stats(argv[1])
      # sns.publish(PhoneNumber=argv[1], Message=output)

  else:
    



######################################################################
# Tweet functions for all months
######################################################################

# def filter_all_tweets(tweets):
#   clinton_tweets = []
#   trump_tweets = []

#   for tweet in tweets:
#     if tweet['is_retweet'] == 'False':
#       if tweet['handle'] == 'HillaryClinton':
#         clinton_tweets.append(tweet)
#       elif tweet['handle'] == 'realDonaldTrump':
#         trump_tweets.append(tweet)

#   return clinton_tweets, trump_tweets

# def compare_all_tweets():
#   tweets = read_tweets()
#   clinton_tweets, trump_tweets = filter_all_tweets(tweets)

#   clinton_stats = get_tweet_stats(clinton_tweets)
#   trump_stats = get_tweet_stats(trump_tweets)

#   return clinton_stats, trump_stats