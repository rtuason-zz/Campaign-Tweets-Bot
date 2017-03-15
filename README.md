Hillary won the popular vote by about three million votes, but how did her popularity fare against Donald Trump's during their campaigns? A dataset on Kaggle (https://www.kaggle.com/benhamner/clinton-trump-tweets) contains thousands of tweets from both presidential candidates during mid-2016, and my bot allows us to examine how popular each one's tweets were given a range of dates.

Using a range of dates, the bot will look at each candidate's total number of tweets, and more importantly, the average tweet's retweet and favorite counts.

Flags:  
--dates  
Provide two dates between 4/17/16 and 9/29/16, which is the range in which both datasets contain tweets from both candidates. If this flag is not used, the bot will give info on the entire range.

--phone  
Provide as many phone numbers as you'd like, barring AWS cost constraints. Each one will receive the info described above

--twitter  
Similar to the phone flag above. Don't include the '@' sign.