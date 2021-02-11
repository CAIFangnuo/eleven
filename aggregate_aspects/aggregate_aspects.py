import pandas as pd
import numpy as np

from ast import literal_eval
from collections import Counter
import argparse
import os

from gensim.models import KeyedVectors

from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(language='english')


# find a number of most frequent words
def find_most_frequent_words(df, number):
    df1 = df.copy()
    df1['topic_sentiment'] = df1['topic_sentiment'].apply(literal_eval)
    d = dict(Counter([item for sublist in df1['topic_sentiment'].apply(
        lambda x:list(x.keys())).tolist() for item in sublist]))
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1],
                                    reverse=True)[:20]}


# find all aspects of one topic
def aggregate(df, aspect, model):
    df1 = df.copy()
    df1['topic_sentiment'] = df1['topic_sentiment'].apply(literal_eval)
    topics = list(set([item for sublist in df1['topic_sentiment'].apply(
        lambda x:list(x.keys())).tolist() for item in sublist]))
    topics_stemmed = [' '.join([stemmer.stem(x)
                                for x in topic.split()]) for topic in topics]
    aspect_topics = [
        topic for topic in topics_stemmed
        if topic in model.vocab and model.similarity(aspect, topic) > 0.4]
    topics_sentiment_opinion = [{key: value} for d in df1['topic_sentiment']
                                for key, value in d.items() if ' '.join(
                                    [stemmer.stem(x) for x in key.split()]
    ) in aspect_topics]
    return topics_sentiment_opinion


# mean value of all sentiments towards one topic
def topic_sentiment_mean(topics_sentiment_opinion):
    return np.mean(
        np.array([list(d.values())[0][0] for d in topics_sentiment_opinion]))


# total number of reviews
def topic_count(topics_sentiment_opinion):
    return len(topics_sentiment_opinion)


# positive and negative count of one topic
def topic_positive_negative_count(topics_sentiment_opinion):
    sentiment = np.array([list(d.values())[0][0]
                          for d in topics_sentiment_opinion])
    return len(sentiment[sentiment > 0]), len(sentiment[sentiment < 0])


# positive opinions of one topic
def topic_positive_opinion(topics_sentiment_opinion):
    opinions = dict(Counter([list(d.values())[
                    0][1] for d in topics_sentiment_opinion if list(
                        d.values())[0][0] > 0]))
    return {k: v for k, v in sorted(
        opinions.items(), key=lambda item: item[1], reverse=True)}


# negative opinions of one topic
def topic_negative_opinion(topics_sentiment_opinion):
    opinions = dict(Counter([list(d.values())[
                    0][1] for d in topics_sentiment_opinion if list(
                        d.values())[0][0] < 0]))
    return {k: v for k, v in sorted(
        opinions.items(), key=lambda item: item[1], reverse=True)}


# extract aspects from one topic
def extract_aspects(topics_sentiment_opinion):
    return list(set(
        [stemmer.stem(list(d.keys())[0]) for d in topics_sentiment_opinion]))


# mean value of sentiments towards each aspect in one topic
def aspects_sentiment_mean(topics_sentiment_opinion):
    result = {}
    for topic in extract_aspects(topics_sentiment_opinion):
        result[topic] = np.mean(
            np.array([list(d.values())[0][0]for d in topics_sentiment_opinion
                      if stemmer.stem(list(d.keys())[0]) == topic]))
    return result


# count of each aspect in one topic
def aspects_count(topics_sentiment_opinion):
    result = {}
    for topic in extract_aspects(topics_sentiment_opinion):
        result[topic] = len(
            [d for d in topics_sentiment_opinion if stemmer.stem(list(
                d.keys())[0]) == topic])
    return result

# positive and negative count of aspects


def aspects_positive_negative_count(topics_sentiment_opinion):
    result = {}
    for topic in extract_aspects(topics_sentiment_opinion):
        sentiment = np.array(
            [list(d.values())[0][0] for d in topics_sentiment_opinion
             if stemmer.stem(list(d.keys())[0]) == topic])
        result[topic] = (len(sentiment[sentiment > 0]),
                         len(sentiment[sentiment < 0]))
    return result


# positive opinions of each aspect in one topic
def aspects_positive_opinion(topics_sentiment_opinion):
    result = {}
    for topic in extract_aspects(topics_sentiment_opinion):
        opinions = dict(Counter(
            [list(d.values())[0][1] for d in topics_sentiment_opinion if list(
                d.values())[0][0] > 0 and stemmer.stem(
                    list(d.keys())[0]) == topic]))
        result[topic] = {k: v for k, v in sorted(
            opinions.items(), key=lambda item: item[1], reverse=True)}
    return result

# negative opnions of each aspect in one topic


def aspects_negative_opinion(topics_sentiment_opinion):
    result = {}
    for topic in extract_aspects(topics_sentiment_opinion):
        opinions = dict(Counter(
            [list(d.values())[0][1] for d in topics_sentiment_opinion if
                list(d.values())[0][0] < 0 and stemmer.stem(list(
                    d.keys())[0]) == topic]))
        result[topic] = {k: v for k, v in sorted(
            opinions.items(), key=lambda item: item[1], reverse=True)}
    return result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path", help="Path to the preprocessed dataset",
        type=str, required=True
    )

    parser.add_argument(
        "--most_freq", help="If specified, will only print the most frequent\
        words and display them up to the number specified",
        type=int, required=False
    )

    parser.add_argument(
        "--topic", help="Specify the topic that you want to analyse",
        type=str, required=False
    )

    args = parser.parse_args()

    model = KeyedVectors.load_word2vec_format(
        'GoogleNews-vectors-negative300.bin.gz', binary=True)
    df = pd.read_csv(args.path)

    if args.most_freq:
        print(find_most_frequent_words(df, args.most_freq))

    if args.topic:

        topics_sentiment_opinion = aggregate(df, args.topic, model)

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               f"results/{os.path.basename(__file__)}-\
                                   {args.topic}.txt"), "w+") as f:
            f.write("Mean Value of all Sentiments towards this topic\n")
            f.write(str(topic_sentiment_mean(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Aggregate Number of Sentiments on that topic\n")
            f.write(str(topic_count(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Positive and Negative count towards that topic\n")
            f.write(str(
                topic_positive_negative_count(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Positive Opinions of that topic\n")
            f.write(str(topic_positive_opinion(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Negative Opinions of that topic\n")
            f.write(str(topic_negative_opinion(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Aspects from that topic\n")
            f.write(str(extract_aspects(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write(
                "Mean Value of Sentiments towards each Aspect in one topic\n")
            f.write(str(aspects_sentiment_mean(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Count of each Aspect in one topic\n")
            f.write(str(aspects_count(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Positive and Negative Count of Aspects\n")
            f.write(
                str(aspects_positive_negative_count(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Positive Opinions of each Aspect in one topic\n")
            f.write(str(aspects_positive_opinion(topics_sentiment_opinion)))
            f.write("\n\n")

            f.write("Negative Opnions of each Aspect in one topic\n")
            f.write(str(aspects_negative_opinion(topics_sentiment_opinion)))
            f.write("\n\n")

        # print("Mean Value of all Sentiments towards this topic")
        # print(topic_sentiment_mean(topics_sentiment_opinion))
        # print("\n")

        # print("Aggregate Number of Sentiments on that topic")
        # print(topic_count(topics_sentiment_opinion))
        # print("\n")

        # print("Positive and Negative count towards that topic")
        # print(topic_positive_negative_count(topics_sentiment_opinion))
        # print("\n")

        # print("Positive Opinions of that topic")
        # print(topic_positive_opinion(topics_sentiment_opinion))
        # print("\n")

        # print("Negative Opinions of that topic")
        # print(topic_negative_opinion(topics_sentiment_opinion))
        # print("\n")

        # print("Aspects from that topic")
        # print(extract_aspects(topics_sentiment_opinion))
        # print("\n")

        # print("Mean Value of Sentiments towards each Aspect in one topic")
        # print(aspects_sentiment_mean(topics_sentiment_opinion))
        # print("\n")

        # print("Count of each Aspect in one topic ")
        # print(aspects_count(topics_sentiment_opinion))
        # print("\n")

        # print("Positive and Negative Count of Aspects")
        # print(aspects_positive_negative_count(topics_sentiment_opinion))
        # print("\n")

        # print("Positive Opinions of each Aspect in one topic")
        # print(aspects_positive_opinion(topics_sentiment_opinion))
        # print("\n")

        # print("Negative Opnions of each Aspect in one topic")
        # print(aspects_negative_opinion(topics_sentiment_opinion))
        # print("\n")


if __name__ == "__main__":
    main()
