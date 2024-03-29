from data_import import read_tweets
from data_export import send_texts, send_tweets
from dateutil import parser as dateparser

import argparse
import re

MIN_DATE = '4/17/16'
MAX_DATE = '9/29/16'  # Include tweets through 9/28/16 11:59pm

######################################################################
# Tweet functions for a range of dates
######################################################################
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
  
  twitter_resp1, twitter_resp2 = create_twitter_response(date1, date2, clinton_stats, trump_stats)

  send_texts(args, response)
  send_tweets(args, twitter_resp1, twitter_resp2)  