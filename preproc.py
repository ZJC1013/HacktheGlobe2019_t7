import sys
import argparse
import os
import json
import numpy as np
import html
import re
import time
import spacy
import string
import csv
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier
from sklearn.svm import SVC
from scipy.sparse import csc_matrix



# indir = '/Users/jasonzhou/Downloads/Hack_data'
# abbv_dir_1 = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/abbrev.english'
# abbv_dir_2 = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/pn_abbrev.english'
# clitics_dir = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/clitics'
# stop_dir = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/StopWords'

indir = 'Hack_data'
abbv_dir_1 = '/u/cs401/Wordlists/abbrev.english'
abbv_dir_2 = '/u/cs401/Wordlists/pn_abbrev.english'
clitics_dir = '/u/cs401/Wordlists/clitics'
stop_dir = '/u/cs401/Wordlists/StopWords'

def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step

    Returns:
        modComm : string, the modified comment
    '''
    # print(comment)
    modComm = ''
    if 1 in steps:
        #Remove all newline characters
        # comment = comment.replace("\n"," ")
        comment = ' '.join([line.strip() for line in comment.strip().splitlines()])
    if 2 in steps:
        #Replace HTML character codes (i.e., &...;) with their ASCII equivalent
        comment = html.unescape(comment)
    if 3 in steps:
        #Remove all URLs (i.e., tokens beginning with http or www)
        comment = re.sub(r'http\S+', '', comment, flags=re.MULTILINE)
        comment = re.sub(r'www\S+', '', comment, flags=re.MULTILINE)
        comment = re.sub(r'@\S+','',comment, flags=re.MULTILINE)
        # comment = re.sub(r'(?:(?:www|http|https):\/\/)?([-a-zA-Z0-9.]{2,256}\.[a-z]{2,4})\b(?:\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?',"",comment,flags=re.MULTILINE)
        # reference: https://stackoverflow.com/questions/38804425/remove-urls-from-a-text-file
    if 4 in steps:
        abbrev_1 = open(abbv_dir_1).read().split('\n')
        abbrev_2 = open(abbv_dir_2).read().split('\n')
        abbreviation = abbrev_1 + abbrev_2
        if '' in abbreviation:
            abbreviation.remove('')
        # punctuation = "!\"#$%&()*+,\\-./:;<=>?@[]^_{|}~"

        temp = ''
        i = 0
        while i < len(comment):
            isException = False
            if i == 0 or not(comment[i-1].isalpha()):
                for word in abbreviation:
                    if comment[i:].lower().startswith(word.lower()):
                        temp += comment[i:i+len(word)]
                        i += len(word)
                        isException = True
                        break
            if not(isException):
                if comment[i] in string.punctuation and comment[i] != "'":
                    temp += ' '
                    while i < len(comment) and (comment[i] in string.punctuation and comment[i] != "'"):
                        temp += comment[i]
                        i += 1
                    temp += ' '
                else:
                    temp += comment[i]
                    i += 1

        comment = temp.replace('  ', ' ')

    if 5 in steps:
        clitics = open(clitics_dir).read().split('\n')
        # clitics.append("'t")
        clitics.append("s'")
        for word in clitics:
            if word == "s'":
                comment = comment.replace(word,"s '")
            else:
                comment = comment.replace(word," "+word)
        # print(comment)

    if 6 in steps:
        # print(comment)
        stop_words = open(stop_dir).read().split('\n')
        stop_words = list(filter(('').__ne__, stop_words))
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        temp = ''
        # print(comment)
        for word in comment:
            if word.lower() not in stop_words:
                temp += word + ' '
        # print(temp)
        comment = temp

    if 7 in steps:
        utt = nlp(comment)
        temp = ''
        for token in utt:
            if token.lemma_.startswith('-'):
                temp += token.text
            else:
                temp += token.lemma_
            temp += ' '
        # print(temp)
        comment = temp

    if 8 in steps:
        comment = comment.lower()

    if 9 in steps:
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        temp = ''
        for word in comment:
            if word.isalpha():
                temp += word + ' '
        comment = temp

    modComm = comment
    return modComm

def buildVolcab(data):
    totalVolcab = []
    for tweet in data:
        volcab = {}
        sent = tweet.split(' ')
        for word in sent:
            if word not in volcab.keys():
                volcab[word] = 1
            else:
                volcab[word] += 1
        totalVolcab.append(volcab)
    return totalVolcab

def buildwordList(totalVolcab):
    wordList = []
    for volcab in totalVolcab:
        for word in volcab.keys():
            if word not in wordList:
                wordList.append(word)
    return wordList

def buildMatrix(wordList, totalVolcab):
    matrix = np.zeros((len(totalVolcab),len(wordList)))
    for i, volcab in enumerate(totalVolcab):
        for j, key_word in enumerate(wordList):
            if key_word in volcab.keys():
                matrix[i][j] = volcab[key_word]
    return matrix


if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description='Process each .')
    # parser.add_argument('ID', metavar='N', type=int, nargs=1,
    #                     help='your student ID')
    # parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    # parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000)
    # args = parser.parse_args()
    # print(args)
    #
    # if (args.max > 200272):
    #     print( "Error: If you want to read more than 200,272 comments per file, you have to read them all." )
    #     sys.exit(1)

    nlp = spacy.load('en', disable=['parser', 'ner'])
    # sents = json.load(open('sents.json'))

    # scores = json.load(open('10scores.json'))
    # wordList = json.load(open('10wordList.json'))
    # # print(type(sents))
    # scoreMatrix = np.array(scores)
    # print(scoreMatrix.shape)
    # matrix = np.load('10matrix.npz')
    # matrix = matrix['arr_0']
    # print(matrix.shape)

    # clf = AdaBoostClassifier()
    # clf.fit(matrix,scoreMatrix)
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            if not file.startswith('.DS_Store'):
                fullFile = os.path.join(subdir, file)
                print( "Processing " + fullFile)

                scores, sents = [], []

                df = pd.read_csv(fullFile,sep='delimiter',header=None)
                indices = np.arange(len(df))
                np.random.shuffle(indices)
                tweet = df.iloc[0,0].split(',')[5]
                j = 0
                for i in range(50000):
                    j += 1
                    if j >= 10000:
                        print(i)
                        j = 0
                    index = indices[i]
                    tweet = df.iloc[index,0].split(',')[5]
                    tweet = tweet.lstrip('\"')
                    tweet = tweet.rstrip('\"')

                    sent = preproc1(tweet,range(1,10))
                    sents.append(sent)

                    score = df.iloc[index,0].split(',')[0]
                    score = score.lstrip('\"')
                    score = score.rstrip('\"')
                    score = int(score) - 2
                    scores.append(score)

                print(len(scores))
                print(len(sents))
                print(len(scores) == len(sents))

    totalVolcab = buildVolcab(sents)
    wordList = buildwordList(totalVolcab)
    matrix = buildMatrix(wordList, totalVolcab)
    print(matrix.shape)
    scoreMatrix = np.array(scores)
    print(scoreMatrix.shape)


    clf = SVC(kernel='linear',max_iter=1000)
    clf.fit(matrix,scoreMatrix)

    test_sentence = "I'm emotional, devastated and I'm distressed, because I can't find anywhere to stay"
    test_sentence = preproc1(test_sentence,range(1,10))
    sent_list = test_sentence.split(' ')
    sent_list = list(filter(('').__ne__, sent_list))
    x_test = np.zeros((len(sent_list),1))
    for word in sent_list:
                if word in wordList:
                    word_index = wordList.index(word)
                    x_test[word_index] += 1
    y_pred = clf.predict(x_test)
    print(y_pred)
