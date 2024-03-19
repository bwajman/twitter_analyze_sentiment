import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
from textblob import TextBlob
from datetime import datetime, timedelta

days=0
for i in range(days+1):
    today = datetime.today() - timedelta(days=i)
    today = today.strftime("%Y%m%d")
    yesterday = datetime.today() - timedelta(days=i+1)
    yesterday = yesterday.strftime("%Y%m%d")

    year_y, month_y, day_y = yesterday[0:4], yesterday[4:6], yesterday[6:8]
    year, month, day = today[0:4], today[4:6], today[6:8]

    query = f"(cardano OR $ada) until:{year}-{month}-{day} since:{year_y}-{month_y}-{day_y}"
    tweets = []

    for tweet in sntwitter.TwitterHashtagScraper(query).get_items():
        # if len(tweets) == 25:
        #     break
        # else:
            tweets.append([tweet.date,tweet.user.username, tweet.content, tweet.hashtags, tweet.user.followersCount, tweet.user.verified, tweet.id])

    df = pd.DataFrame([tweet for tweet in tweets], columns = ['Date','User','Content','Hashtags','Followers','Verified','ID'])

    def cleanText(text):
        text = re.sub(r'@[A-Za-z0-9]+','',text) #remove mentions
        text = re.sub(r'#', '', text) #remove #
        text = re.sub(r'RT[\s]+', '', text) #remove RT
        text = re.sub(r'https?:\/\/\S+', '', text) #remove hyperlink
        text = re.sub(r'\n', '', text)  #remove enter
        return text

    def getPolarity(text):
        return TextBlob(text).sentiment.polarity

    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    def getSentiment(polarity):
        if polarity < 0:
            return 'Negative'
        elif polarity > 0:
            return 'Positive'
        elif polarity == 0:
            return 'Neutral'

    df['Content'] = df['Content'].apply(cleanText)
    df['Subjectivity'] = df['Content'].apply(getSubjectivity)
    df['Polarity'] = df['Content'].apply(getPolarity)
    df['Sentiment'] = df['Polarity'].apply(getSentiment)

    df.loc[df['Hashtags'].isna(), 'Hashtags'] = 'None'

    df = df.set_index('ID')

    file_daily=f'C:\data\crypto\cardano_{yesterday}.csv'
    df.to_csv(file_daily, sep='\t')

    file="C:\data\crypto\overall.txt"
    # DATE | COUNT | POSITIVE | NEGATIVE | NEUTRAL | VERIFIED | FOLLOWERS PER TWEET
    count = df['Content'].count()
    positive=df['Content'][(df['Sentiment'] == 'Positive')].count()
    negative=df['Content'][(df['Sentiment'] == 'Negative')].count()
    neutral=int(count)-int(positive)-int(negative)
    verified=df['Content'][(df['Verified'] == True)].count()
    followers=df['Followers'].sum()/count
    with open(file, "a") as file_object:
        file_object.write(f"{yesterday};{count};{positive};{negative};{neutral};{verified};{followers}\n")
