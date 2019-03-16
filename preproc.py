import sys
import argparse
import os
import json
# import numpy as np
import html
import re
import time
import spacy
import string

indir = '/u/cs401/A1/data/'
abbv_dir_1 = '/u/cs401/Wordlists/abbrev.english'
abbv_dir_2 = '/u/cs401/Wordlists/pn_abbrev.english'
clitics_dir = '/u/cs401/Wordlists/clitics'
stop_dir = '/u/cs401/Wordlists/StopWords'

# indir = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/data/'
# abbv_dir_1 = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/abbrev.english'
# abbv_dir_2 = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/pn_abbrev.english'
# clitics_dir = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/clitics'
# stop_dir = '/Users/jasonzhou/Downloads/CSC401_NLP_origin/A1/Wordlists/StopWords'

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
        utt = nlp(comment)
        # for token in utt:
        #     print(token.text, token.lemma_, token.pos_, token.tag_)
        temp = ''
        for token in utt:
            temp += token.text + "/" + token.tag_
            temp += ' '
        comment = temp
        # print(comment)

    if 7 in steps:
        # print(comment)
        stop_words = open(stop_dir).read().split('\n')
        stop_words = list(filter(('').__ne__, stop_words))
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        temp = ''
        # print(comment)
        for word in comment:
            word2 = word.split('/')
            if word2[0].lower() not in stop_words:
                temp += word + ' '
        # print(temp)
        comment = temp

    if 8 in steps:
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        origin_comment = ''
        for word in comment:
            origin_comment += word.split('/')[0] + ' '
        # print(origin_comment)
        utt2 = nlp(origin_comment)
        temp = ''
        for token in utt2:
            if token.lemma_.startswith('-'):
                temp += token.text + "/" + token.tag_
            else:
                temp += token.lemma_ + "/" + token.tag_
            temp += ' '
        # print(temp)
        comment = temp

    if 9 in steps:
        temp = ''
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        # print(comment)
        for i, word in enumerate(comment):
            if '/' in word:
                if word.split('/')[-1] == '.' and i != len(comment)-1:
                    if comment[i+1].split('/')[0].isalpha():
                        temp += word + '\n' + ' '
                    else:
                        temp += word + ' '
                else:
                    temp += word + ' '
        comment = temp
        # print(comment)

        # origin_comment = ''
        # for word in comment:
        #     origin_comment += word.split('/')[0] + ' '
        # print(origin_comment)
        # nlp = spacy.load('en')

        # doc = nlp(origin_comment)
        # temp = ''
        # for sent in doc.sents:
        #     # print(sent.text  + '\n')
        #     for word in sent:
        #         if word.lemma_.startswith('-'):
        #             temp += word.text + "/" + word.tag_
        #         else:
        #             temp += word.lemma_ + "/" + word.tag_
        #         temp += " "
        #     temp += "\n"

        # temp = ''
        # for word in doc:
        #     temp += word.text + "/" + word.tag_
        #     if word.is_sent_start == True:
        #         temp += '\n'
        #     else:
        #         # if word.text.isalpha():
        #         temp += ' '
        # print(temp)
        # comment = temp

    if 10 in steps:
        temp = ''
        comment = comment.split(" ")
        comment = list(filter(('').__ne__, comment))
        # print(comment)
        for word in comment:
            # print(word)
            temp += word.split('/')[0].lower() +'/'+ word.split('/')[1] + ' '
        comment = temp
        # print(comment)

    modComm = comment
    return modComm

def main( args ):
    tic = os.times()[0]
    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        # files = [files[3]]# to-be-deleted
        for file in files:
            fullFile = os.path.join(subdir, file)
            print( "Processing " + fullFile)

            data = json.load(open(fullFile))

            # TODO: select appropriate args.max lines
            # data_sample = np.random.choice(data, args.max, replace=False)

            # data_sample = data[0:args.max]
            # random selection (not required)
            # indices = np.random.choice(len(data),args.max)
            # print(indices[0:10])
            # data_sample = [data[i] for i in indices]

            # print("data_sample_length", len(data_sample))
            # print("data", data_sample[0])

            ID = args.ID[0]
            print(ID)
            sample_index = ID % len(data)
            print(sample_index + args.max)
            print(len(data))
            data_sample = data[sample_index : sample_index+args.max]

            # TODO: read those lines with something like `j = json.loads(line)`
            data_sample_line = [json.loads(data_sample[i]) for i in range(len(data_sample))]
            # print("data_sample_line_length", len(data_sample))
            # print("data_line", data_sample_line[0:2])

            # TODO: choose to retain fields from those lines that are relevant to you
            # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...)
            print(len(data_sample_line))
            for i in range(len(data_sample_line)):
                data_sample_line[i]= {k: v for k, v in data_sample_line[i].items() if k == 'id' or k == 'body'}
                data_sample_line[i]['cat'] = file
            # print("data_sample_line_length", len(data_sample))
            # print("data_line", data_sample_line[0:2])

            # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
            # TODO: replace the 'body' field with the processed text
            # TODO: append the result to 'allOutput'


            for i in range(len(data_sample_line)):
            # for i in range(1):
                data_sample_line[i]['body'] = preproc1(data_sample_line[i]['body'],range(1,11))
                allOutput.append(json.dumps(data_sample_line[i]))
                print("finished line: ", i)
                toc = os.times()[0]
                print("run time:",toc-tic)

            # ex_sent = "'Hi!' says John, 'I'm going to see your cats' dogs e.g.' e.g. Monday cohort. Tuesday session."
            # sent = preproc1(ex_sent,range(1,11))
            # print(sent)
            # print("data_line_proc", data_sample_line[0]['body'])
            toc = os.times()[0]
            print("final run time:",toc-tic)

    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()
    print(args)

    if (args.max > 200272):
        print( "Error: If you want to read more than 200,272 comments per file, you have to read them all." )
        sys.exit(1)

    nlp = spacy.load('en', disable=['parser', 'ner'])
    main(args)
    # python a1_preproc.py 999123456 -o preproc.json
    # python a1_preproc.py 1003300545 -o preproc.json
