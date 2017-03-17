import re
import json
import boto3
from twython import Twython

######################################################################
# Send response as texts or tweets, if applicable
######################################################################
def send_texts(args, response):
  if args.phone:
    phone_pattern = re.compile("^\d{10}$")
    for phone_number in args.phone:
      if not phone_pattern.match(phone_number):
        print("At least one phone number has been formatted incorrectly. Phone numbers must contain exactly ten numbers.")
        return   # Don't exit program. There might be Twitter handles.

    session = boto3.Session(profile_name='default')
    sns = session.client('sns')
    for phone_number in args.phone:
      sns.publish(PhoneNumber='+1' + phone_number, Message=response)

def send_tweets(args, twitter_resp1, twitter_resp2) :
  if args.twitter:
    twitter_pattern = re.compile("^[\w]{1,15}$")
    for handle in args.twitter:
      if not twitter_pattern.match(handle):
        print("At least one Twitter handle has been formatted incorrectly.")
        return

    with open('twitter-creds.json') as f:
      creds = json.load(f)

    client = Twython(creds['consumer_key'], creds['consumer_secret'], creds['access_token'], creds['access_token_secret'])

    for handle in args.twitter:
      msg1 = "@{} {}".format(handle, twitter_resp1)
      msg2 = "@{} {}".format(handle, twitter_resp2)
      client.update_status(status=msg1)
      client.update_status(status=msg2)