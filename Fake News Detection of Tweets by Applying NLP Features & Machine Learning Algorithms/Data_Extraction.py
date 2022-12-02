import json
import pandas as pd
import os
import tweepy
from ast import literal_eval
import numpy as np
import contractions
import nltk
import string

# Display all the data
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Read CSV and Store into Pandas Dataframe
gossipcop_fakenews = pd.DataFrame(pd.read_csv(r'C:\Users\chinp\Desktop\FakeNewsNet-master\dataset\gossipcop_fake.csv'))
gossipcop_realnews = pd.DataFrame(pd.read_csv(r'C:\Users\chinp\Desktop\FakeNewsNet-master\dataset\gossipcop_real.csv'))
politifact_fakenews = pd.DataFrame(pd.read_csv(r'C:\Users\chinp\Desktop\FakeNewsNet-master\dataset\politifact_fake.csv'))
politifact_realnews = pd.DataFrame(pd.read_csv(r'C:\Users\chinp\Desktop\FakeNewsNet-master\dataset\politifact_real.csv'))

# # Add new columns as target variable
gossipcop_fakenews['target'] = 1
gossipcop_realnews['target'] = 0
politifact_fakenews['target'] = 1
politifact_realnews['target'] = 0

# Concatenate all dataframes into 1 dataframe. ignore_index was used to Clear the existing index and reset it
dataset = pd.concat([gossipcop_realnews,gossipcop_fakenews,politifact_realnews,politifact_fakenews], ignore_index=True)

# News Content Extraction
dataset['news_content'] = None
directory = r'C:/Users/chinp/Desktop/FakeNewsNet-master/code/fakenewsnet_dataset'
source = [r'/gossipcop', r'/politifact']
newstype = [r'/fake', r'/real']
jsonfile = r'/news content.json'

for i in source:
    for j in newstype:
        for filename in os.listdir(directory+i+j):
            path = directory + i + j + '/' + filename + jsonfile
            try:
                file_object = open(path, 'r')
                file_content = file_object.read()
                data = json.loads(file_content)

                dataset.loc[dataset['id'] == filename, 'news_content'] = data['text']

            except:
                pass


# remove the empty news content
# dataset = dataset[dataset["news_content"].notnull()]
# dataset = dataset[dataset["news_content"] != '']

# Twitter Attributes Extraction

# Replace null with empty string
dataset['tweet_ids'][dataset['tweet_ids'].isnull()] = ''

# Split tweet id into individual ids separated by tab character
dataset['split_ids'] = dataset['tweet_ids'].str.split('\t')

# join all tweet_ids into one row due to few rows have duplicated news_url but different tweet_ids
dataset = dataset.groupby('news_url').agg({'id': 'first', 'title': 'first', 'target': 'first', 'text': ' first',
                                           'news_content': 'first', 'split_ids': 'sum'}).reset_index()

# keep the unique tweet ids
dataset['split_ids'] = dataset['split_ids'].map(np.unique)

# convert the array to list
dataset['split_ids'] = dataset['split_ids'].apply(list)

dataset[['id', 'split_ids']].to_csv('id_tweetID.csv', index=False)

ACCESS_TOKEN = '194482094-gWMT2EaulNtTXpyTmGUU7KLzGP2NjD18R0XHkXgx'
ACCESS_SECRET = 'uQ1OuA0oPXqYZPAUKkZkyr8kq0roGDosNmURCK2SzFIr2'
CONSUMER_KEY = '7Gv9i4PDY0Vtt1k6i04rf1p6d'
CONSUMER_SECRET = '0GNvpA89eMyUuJiG6TVT0R2x1YcdPs0NTQSTkzEdGB76ZPOVEp'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,
                 compression=True)

# reading the dataset from csv file
dataset = pd.read_csv(r'C:\Users\chinp\PycharmProjects\pythonProject\id_tweetID.csv')

# convert string back to list
dataset['split_ids'] = dataset['split_ids'].apply(literal_eval)

news_id = []
num_ids = []
retweets = []
favorites = []
avail_tweet = []
avail_ids = []

# loop through every record
for i in range(len(dataset)):

    total_retweets = 0
    total_favorites = 0
    avail_tweets = 0

    # store tweet_ids into ids
    ids = dataset.iloc[i, 1]

    if ids[0] == '':  # if empty, all null values (to be imputed later on)
        news_id.append(dataset.iloc[i, 0])
        num_ids.append(None)
        retweets.append(None)
        favorites.append(None)
        avail_tweet.append(None)
        avail_ids.append(None)

    else:
        length = len(ids)  # count how many ids

        loops = (length + 98) // 99  # count number of loops needed (tweepy only allows
        # 100 extractions at a single time)
        for j in range(loops):
            if j + 1 == loops:
                data = ids  # final loop contains all remaining data

            else:
                data = ids[0:99]  # take first 99 data of every loop
                del (ids[0:99])  # remove first 99 data as its already been looped through

            tweets = api.statuses_lookup(data)  # fetch data from Twitter

            for tweet in tweets:  # loop through each set of data to compute the totals
                total_retweets += tweet.retweet_count
                total_favorites += tweet.favorite_count
                avail_tweets += 1

        news_id.append(dataset.iloc[i, 0])
        num_ids.append(length)
        retweets.append(total_retweets)
        favorites.append(total_favorites)
        avail_tweet.append(avail_tweets)
        avail_ids.append(avail_tweets / length)

# put the values into a dataframe
df = pd.DataFrame({'id': news_id,
                   'total_retweets': retweets,
                   'total_favorites': favorites,
                   'total_ids': num_ids,
                   'total_available_ids': avail_tweet,
                   'percentage_avai_ids': avail_ids
                   })

# output data to a csv file
df.to_csv('tweet_attributes.csv', index=False)

# Linguistic Attributes

# _________________________ Deriving URL and Title Words Attributes __________________________________
# change the null values in news url into empty string
dataset['news_url'][dataset['news_url'].isnull()] = ''


# a function to remove the URL protocol
def remove_url_protocol(url):
    if url.startswith('http'):
        return url[6:]
    elif url.startswith('https'):
        return url[7:]
    else:
        return url


# create a new attribute in data frame which does not contains URL protocol
dataset['no_url_protocol'] = dataset['news_url'].apply(remove_url_protocol)


# a function to check whether have www or not
def www_function(url):
    if url.startswith('www'):
        return 1
    else:
        return 0


# create a new attribute in a data frame which check whether have www or not
dataset['url_www'] = dataset['no_url_protocol'].apply(www_function)


# a function that count the url level
def url_level(url):
    return url.count('/') + 1


# create a new attribute to count the url level
dataset['url_level'] = dataset['no_url_protocol'].apply(url_level)

# _________________________ Text Preprocessing __________________________________

# replace the next line in news content into blank space
dataset['news_content'] = dataset['news_content'].replace('\n', ' ', regex=True)

# count the number of sentences which is the punctuation is end by the question mark, full stop and exclamation mark
dataset['total_sentences'] = dataset['news_content'].str.count('\.') + dataset['news_content'].str.count('\!') + \
                             dataset['news_content'].str.count('\?')

# remove rows with no sentences
dataset = dataset[dataset['total_sentences'] != 0]

# expand the contradictions in the news content (exp: I've will become I have)
dataset['news_content'] = dataset['news_content'].apply(contractions.fix)

# convert all the news content into lowercase
dataset['news_content_lowercase'] = dataset['news_content'].str.lower()

# split the paragraph into each individual words
dataset['individual_words'] = dataset['news_content_lowercase'].str.split()

# initialize lemmatizer
lemmatizer = nltk.WordNetLemmatizer()

# create a function to perform lemmatization of words
def lemmatize(a):
    a = [lemmatizer.lemmatize(word) for word in a]
    return a


dataset = dataset.assign(lemmatized_words=dataset.individual_words.apply(lambda a: lemmatize(a)))

# count the total number of words in the news content
dataset['word_size'] = dataset['news_content'].str.split().apply(len)

# average number of words in each sentence
dataset['avg_word_per_sentence'] = dataset['word_size']/dataset['total_sentences']

# number of words in title
dataset['no_of_words_in_title'] = dataset['title'].str.split().apply(len)


def count_punctuation(news_content):
    count = 0
    for i in range(0, len(news_content)):
        # Checks whether given character is a punctuation mark
        if news_content[i] in string.punctuation:
            count = count + 1
    return count


dataset['count_punct'] = dataset['news_content'].apply(count_punctuation)

# _________________________ Deriving Linguistic Attributes __________________________________

# POS Tagger for each individual words
dataset['pos_taggers'] = dataset['lemmatized_words'].apply(nltk.pos_tag)


# Functon to count the POS Tagger
def count_pos_taggers(word):
    count = [0 for x in range(7)]
    for token, tag in word:
        if tag.startswith('NN') or tag.startswith('PR'):
            count[0] += 1
        elif tag.startswith('VB') or tag.startswith('MD'):
            count[1] += 1
        elif tag.startswith('JJ'):
            count[2] += 1
        elif tag.startswith('RB'):
            count[3] += 1
        elif tag.startswith('IN') or tag.startswith('TO'):
            count[4] += 1
        elif tag.startswith('CC'):
            count[5] += 1
        elif tag.startswith('UH'):
            count[6] += 1
    return count


dataset['total_pos_tagger'] = dataset['pos_taggers'].apply(count_pos_taggers)

# split all pos tagger into individual columns
total_pos_tagger = (dataset['total_pos_tagger'].transform([lambda x:x[0], lambda x:x[1], lambda x:x[2], lambda x:x[3],
                                                           lambda x:x[4], lambda x:x[5], lambda x:x[6]])
                    .set_axis(['noun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'interjection'],
                              axis=1, inplace=False))

# merge the pos tagger dataframe with the dataset dataframe
dataset = pd.concat([dataset, total_pos_tagger], axis=1)

# Count density of noun
dataset['noun_density'] = dataset['noun'] / dataset['word_size']

# Count density of verb
dataset['verb_density'] = dataset['verb'] / dataset['word_size']

# Count density of adjective
dataset['adjective_density'] = dataset['adjective'] / dataset['word_size']

# Count density of adverb
dataset['adverb_density'] = dataset['adverb'] / dataset['word_size']

# Count density of preposition
dataset['preposition_density'] = dataset['preposition'] / dataset['word_size']

# Count density of conjunction
dataset['conjunction_density'] = dataset['conjunction'] / dataset['word_size']

# Count density of interjection
dataset['interjection_density'] = dataset['interjection'] / dataset['word_size']

enhanced_dataset = dataset[['id', 'news_url', 'target', 'url_protocol', 'url_www', 'url_level', 'total_sentences', 'word_size',
                            'avg_word_per_sentence', 'no_of_words_in_title', 'count_punct', 'noun', 'verb', 'adjective', 'adverb',
                            'preposition', 'conjunction', 'interjection', 'noun_density', 'verb_density', 'adjective_density',
                            'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density']]

# read tweet_attributes dataset
tweet_attributes = pd.read_csv(r'tweets_attributes.csv')

# merge tweet_attributes with enhanced dataset
enhanced_dataset = pd.merge(enhanced_dataset, tweet_attributes, on=['id'])

# write to csv
dataset.to_csv('enhanced_dataset.csv', index=False)
