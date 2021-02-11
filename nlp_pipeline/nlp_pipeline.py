from nltk.corpus import opinion_lexicon
from gensim.parsing.preprocessing import remove_stopwords
from gensim.utils import simple_preprocess
import nltk
import pandas as pd
import argparse
import os


import spacy
nlp = spacy.load("en_core_web_sm")

nltk.download('stopwords')


nltk.download('opinion_lexicon')

neg = list(opinion_lexicon.negative()) + ['small', 'little', 'tiny']
pos = list(opinion_lexicon.positive())


def pre_processing(df, title_col, review_col):
    if title_col is None:
        df['all_review'] = df[review_col]
    else:
        df['all_review'] = df[title_col] + df[review_col]
    df['all_review'] = df['all_review'].apply(
        lambda x: simple_preprocess(x, deacc=True))
    df['preprocess_data'] = df['all_review'].apply(' '.join)
    df['preprocess_data'] = df['preprocess_data'].apply(
        lambda x: remove_stopwords(x))
    return df


def feature_sentiment(sentence, pos, neg):
    '''
    input: dictionary and sentence
    function: appends dictionary with new features if the feature
              did not exist previously,then updates sentiment to
              each of the new or existing features
    output: updated dictionary
    '''
    sent_dict = dict()
    sentence = nlp(sentence)
    opinion_words = neg + pos
    debug = 0
    for token in sentence:
        # check if the word is an opinion word, then assign sentiment
        if token.text in opinion_words:
            sentiment = 1 if token.text in pos else -1
            # if target is an adverb modifier (i.e. pretty, highly, etc.),
            # ignore and pass
            if (token.dep_ == "advmod"):
                continue
            elif (token.dep_ == "amod"):
                sent_dict[token.head.text] = (sentiment, token.text)
            # for opinion words that are adjectives, adverbs, verbs...
            else:
                for child in token.children:
                    # if there's a adj modifier (i.e. very, pretty, etc.)
                    # add more weight to sentiment
                    # This could be better updated for modifiers that either
                    # positively or negatively emphasize
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")) \
                            and (child.text in opinion_words):
                        sentiment *= 1.5
                    # check for negation words and flip the sign of sentiment
                    if child.dep_ == "neg":
                        sentiment *= -1
                for child in token.children:
                    # if verb, check if there's a direct object
                    if (token.pos_ == "VERB") & (child.dep_ == "dobj"):
                        sent_dict[child.text] = (sentiment, token.text)
                        # check for conjugates (a AND b), then add both
                        # to dictionary
                        subchildren = []
                        conj = 0
                        for subchild in child.children:
                            if subchild.text == "and":
                                conj = 1
                            if (conj == 1) and (subchild.text != "and"):
                                subchildren.append(subchild.text)
                                conj = 0
                        for subchild in subchildren:
                            sent_dict[subchild] = (sentiment, token.text)

                # check for negation
                for child in token.head.children:
                    noun = ""
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")) \
                            and (child.text in opinion_words):
                        sentiment *= 1.5
                    # check for negation words and flip the sign of sentiment
                    if (child.dep_ == "neg"):
                        sentiment *= -1

                # check for nouns
                for child in token.head.children:
                    noun = ""
                    if (child.pos_ == "NOUN") and (child.text
                                                   not in sent_dict):
                        noun = child.text
                        # Check for compound nouns
                        for subchild in child.children:
                            if subchild.dep_ == "compound":
                                noun = subchild.text + " " + noun
                        sent_dict[noun] = (sentiment, token.text)
                    debug += 1
    return sent_dict


def generate_topic_sentiment(df, title_col, review_col):
    df = pre_processing(df, title_col, review_col)
    df['topic_sentiment'] = df['preprocess_data'].apply(
        lambda x: feature_sentiment(x, pos, neg))
    return df


def main():

    parser = argparse.ArgumentParser()

    # Take the path of the file as a flag in the command line
    parser.add_argument(
        "--path", help="Path to the dataset",
        type=str, required=True
    )

    title_col = 'review_title'
    review_col = 'review_text'

    args = parser.parse_args()

    # create a df out of the csv and get rid of any "floats" (referring to nan)
    df1 = pd.read_csv(args.path)
    df1 = df1.fillna("")

    # create the df including the sentiment
    output = generate_topic_sentiment(df1, title_col, review_col)

    # save new csv in the same folder with new name
    save_path = os.path.join(os.path.dirname(os.path.dirname(
        __file__)),
        f"data_processed/nlp_pipeline_{os.path.basename(args.path)}")
    output.to_csv(save_path)


if __name__ == "__main__":
    main()
