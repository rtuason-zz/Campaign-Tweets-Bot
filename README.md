Hillary won the popular vote by about three million votes, but how did her popularity fare against Donald Trump's during their campaigns? Attending a left-leaning college in a left-leaning area of California has undoubtedly skewed my view of how the general public feels about certain issues, given that I had attributed my opinions to common sense or clear-cut logic for a very long time, so I wanted to get a better look into how Americans on social media felt about each candidate over the course of several months.

A dataset on Kaggle (https://www.kaggle.com/benhamner/clinton-trump-tweets) contains thousands of tweets from both presidential candidates between April and September of 2016, and given a range of dates, this bot allows us to examine how popular each one's tweets were.

Using such a range, the bot will look at each candidate's total number of tweets, and more importantly, the average tweet's retweet and favorite counts. While this method cannot fully capture each candidate’s popularity over time, it at least captures some aspect that we can quantify.

Playing around with this bot using various date ranges has affirmed what I realized when Donald Trump won the presidency: he’s a lot more popular than I had previously believed. Sure, Hillary Clinton may not have been the most beloved presidential candidate in recent history, but I had believed that it was blatantly obvious that she would do a much better job than Trump.

## Notes
The dataset contains tweets from Donald Trump starting in January, while it contains tweets from Hillary Clinton starting in April. To provide a valid comparison, the bot accepts starting dates from 4/17/16, which is when Clinton’s tweets start appearing in the dataset.

One of the most interesting aspects of this bot is its acceptance of flags that allow for greater flexibility in terms of dates examined and output channels desired.

## Flags
#### --dates ####
Provide two dates between 4/17/16 and 9/29/16, which is the range in which both datasets contain tweets from both candidates. If this flag is not used, the bot will give info on the entire range.

#### --phone ####
Provide as many phone numbers (US only) as you'd like, barring AWS cost constraints. Each one will receive the info described above as a text. Every number must be composed of ten digits.

#### --twitter ####
Similar to the phone flag above. Don't include the '@' sign.

## Usage Example
python bot.py --dates 5/12/16 8/23/16 --phone 8001234567 --twitter cal_incidents