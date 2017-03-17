from os import makedirs
from os.path import exists
from os.path import join
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import csv

SRC_URL = 'http://stash.compciv.org/2017/kaggletrumptweets.zip'
DATA_DIR = 'data'
RAW_FILENAME = 'campaign_tweets.csv'

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