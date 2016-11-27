import nltk
import string
from math import *
import operator
from nltk.stem.snowball import GermanStemmer, EnglishStemmer
import nltk.data

import numpy

nltk.data.path.append('./nltk_data/')

MAX_SUMMARY_LENGTH = 400


class CrushedIceSummarizer(object):

    def summarize(self, article, details = False):
        try:
            language = article['language']
        except KeyError:
            language = 'de'

        assert language in ['de', 'en']

        if language == 'en':
            stemmer = EnglishStemmer()
            sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
            additional_stopwords = []

            def valid_word(current_word):
                return current_word not in unicode(string.punctuation) \
                       and current_word not in unicode(nltk.corpus.stopwords.words('english')) \
                       and current_word not in additional_stopwords

        elif language == 'de':
            stemmer = GermanStemmer()
            additional_stopwords = [u'dass']
            sent_detector = nltk.data.load('tokenizers/punkt/german.pickle')

            def valid_word(current_word):
                return current_word not in unicode(string.punctuation) \
                       and current_word not in unicode(nltk.corpus.stopwords.words('german')) \
                       and current_word not in additional_stopwords

        def tf(word, wordlist):
            return float(wordlist.count(word)) / float(len(wordlist))

        # initialize data
        wordlist = []
        bigramlist = []

        # Extract sentences
        sentences = sent_detector.tokenize(article["text"])
        original_sentences = sentences[:]

        for sindex in range(len(sentences)):
            # Extract words
            sentences[sindex] = nltk.word_tokenize(sentences[sindex])

            # Stem words
            for windex in range(len(sentences[sindex])):
                current_word = stemmer.stem(sentences[sindex][windex])
                sentences[sindex][windex] = current_word

                if valid_word(current_word):
                    wordlist.append(current_word)

            # Get bigrams
            sbigrams = nltk.bigrams(sentences[sindex])
            sbigrams = [sbigram for sbigram in sbigrams if valid_word(sbigram[0]) and valid_word(sbigram[1])]
            bigramlist.extend(sbigrams)

        # Make to set -> unique words
        words = set(wordlist)

        # Cluster the text
        # setup observation matrix for k-means
        obs = numpy.zeros((len(sentences), len(words)))

        # Make a lookup dictionary for the words
        # taking .index(word) gives column of the matrix 1..n
        wordlookup = list(words)

        for sindex in range(len(sentences)):
            for windex in range(len(sentences[sindex])):
                if valid_word(sentences[sindex][windex]):
                    wordindex = wordlookup.index(sentences[sindex][windex])
                    obs[sindex][wordindex] += 1.0

        # weight the words according to their tfidf
        weights = numpy.zeros(len(wordlookup))
        for word in wordlookup:
            weights[wordlookup.index(word)] = tf(word, wordlist)

        bigramlist = [' '.join(bigram) for bigram in bigramlist]
        bigrams = set(bigramlist)

        # use dictionary for lookup
        words_tf = {}
        bigrams_tf = {}

        for word in words:
            # calculate term frequency
            words_tf[word] = tf(word, wordlist)

        for bigram in bigrams:
            bigrams_tf[bigram] = tf(bigram, bigramlist)

        # Prepare heading for analysis
        headerwordlist = []
        heading_words = nltk.word_tokenize(article["title"])

        for windex in range(len(heading_words)):
            current_word = stemmer.stem(heading_words[windex])
            if valid_word(current_word):
                headerwordlist.append(current_word)

        headerwords = set(headerwordlist)
        headerlength = len(heading_words)

        # Calculate value for each sentences
        # http://research.nii.ac.jp/ntcir/workshop/OnlineProceedings3/NTCIR3-TSC-SekiY.pdf
        factors = {
            0: 0.17, 1: 0.23, 2: 0.14, 3: 0.08, 4: 0.05, 5: 0.04, 6: 0.06, 7: 0.04, 8: 0.04, 9: 0.15
        }
        sentences_count = len(sentences)

        scores = []

        for sindex in range(sentences_count):
            sentence = sentences[sindex]

            # Factor tfidf
            words_tfidf = 0.0
            words_heading = 0.0
            for word in sentence:
                if valid_word(word):
                    words_tfidf += words_tf[word]
                    if word in headerwords:
                        words_heading += 1./float(headerlength)

            # Factor sentence position
            position = floor(float(sindex) / float(sentences_count)*10)
            sentence_position = factors[position]

            # Total character count in sentence
            character_count = len(original_sentences[sindex])
            if character_count > 350:
                ccfactor = 0.0
            else:
                ccfactor = 1.0

            # first sentence
            if sindex == 0:
                fsfactor = 0.3
            else:
                fsfactor = 0.0

            # Calculate sentence score
            score = (words_tfidf + words_heading) * (0.33 + 0.66*sentence_position) * ccfactor + fsfactor

            scores.append([sindex,
                           score,
                           character_count,
                           words_tfidf,
                           words_heading,
                           sentence_position,
                           ccfactor,
                           1])

        # sort sentences by score
        scores.sort(key=operator.itemgetter(1))
        scoresstore = scores[:]

        summary_indices = []
        summary_length = 0

        while summary_length < MAX_SUMMARY_LENGTH and len(scores) > 0:
            item = scores.pop()
            summary_length += item[2]
            summary_indices.append(item[0])

        # create summary
        summary = {}
        textsummary = ""
        summary["sentences"] = []
        for sindex in range(len(original_sentences)):
            # find scores object
            for s in range(len(scoresstore)):
                if scoresstore[s][0] == sindex:
                    thisscore = scoresstore[s]

            summary["sentences"].append({
                    "sentence": original_sentences[sindex],
                    "included": "yes" if sindex in summary_indices else "no",
                    "score": {
                        "id": thisscore[0],
                        "score": "{:10.4f}".format(thisscore[1]),
                        "words_tfidf": "{:10.4f}".format(thisscore[3]),
                        "words_heading": "{:10.2f}".format(thisscore[4]),
                        "sentence_position": thisscore[5],
                        "ccfactor": thisscore[6],
                        "cluster": str(thisscore[7])
                    }
                })

            if sindex in summary_indices:
                textsummary += original_sentences[sindex] + " "

        summary["textsummary"] = textsummary
        if details:
            return summary
        else:
            return textsummary
