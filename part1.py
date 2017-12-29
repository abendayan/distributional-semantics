import time
from math import sqrt, log
from collections import defaultdict, Counter
WORDS = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar", "piano"]
CONTENT_CLASSES = ['JJ','JJR','JJS','NN','NNS','NNP','NNPS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ','WRB']
PATH_FILE = "wikipedia.sample.trees.lemmatized"
start_time = time.time()
THRESHOLD = 100
SIMILAR = 20
MIN_CO = 0

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

class Corpus:
    def __init__(self):
        self.context_words = {}
        self.context_words_two = {}
        self.context_words_dep = {}
        self.context_words_pmi = {}
        self.context_words_two_pmi = {}
        self.context_words_dep_pmi = {}
        self.words = {}
        self.words_to_ix = {  }
        self.words_count = {}
        self.features_dep = {}
        self.features_dep_to_ix = {}
        self.define_data()
        print "read all of the data " + str(passed_time(start_time))
        self.find_similar_words_in_sentence()
        print "found similar words in sentence " + str(passed_time(start_time))
        self.find_similar_words_in_window()
        print "found similar words in window " + str(passed_time(start_time))

    def find_similar_words_in_sentence(self):
        self.helper_find(self.context_words_pmi)

    def find_similar_words_in_window(self):
        self.helper_find(self.context_words_two_pmi)

    def helper_find(self, dictionnary):
        for test_word in WORDS:
            id_word = self.words[test_word]
            print test_word
            print "___________"
            count_word = dictionnary[id_word]
            close_words = []
            DT = self.dot_product(id_word, count_word)
            for id_target, pmi in count_word.iteritems():
                if id_target != id_word:
                    dist_word = DT[id_target] / (sqrt(self.sum_square(id_word) * self.sum_square(id_target)))
                    if len(close_words) < SIMILAR:
                        close_words.append((id_target, dist_word))
                    else:
                        for i, (temp_word, temp_dist) in enumerate(close_words):
                            if temp_dist < dist_word:
                                close_words[i] = (id_target, dist_word)
                                break
            for temp_word, dist in close_words:
                print self.words_to_ix[temp_word] + " || " + str(dist)
            print "================="

    def sum_square(self, id_word):
        count_word = self.context_words[id_word]
        total = 0.0
        for pmi in count_word:
            total += pmi
        return total

    def dot_product(self, id_word, count_word):
        DT = {}
        for att_id, att_pmi in count_word.iteritems():
            for v_id, v_pmi in self.context_words_pmi[att_id].iteritems():
                if v_id not in DT:
                    DT[v_id] = 0.0
                DT[att_id] = DT[v_id] + att_pmi*v_pmi
        return DT

    def define_data(self):
        start_time = time.time()
        words = open(PATH_FILE, "r").read().split("\n")
        sentences = []
        sentence = []
        dependencies = []
        two_words_windows = []
        all_deps = []
        deps = []
        prev_prev_word = None
        prev_word = None
        total_count = 0.0
        for i, word in enumerate(words):
            if word != "" and len(word) > 1:
                ID, FORM, LEMMA, CPOSTAG, POSTAG, FEATS, HEAD, DEPREL, PHEAD, PDEPREL = word.split()
                vector = {
                # "ID":ID,
                "LEMMA":LEMMA,
                "POSTAG":POSTAG,
                "HEAD":HEAD,
                "DEPREL":DEPREL,
                }
                dependencies.append(vector)
                if POSTAG in CONTENT_CLASSES:
                    if LEMMA not in self.words:
                        self.words[LEMMA] = len(self.words)
                        # self.words_to_ix[self.words[LEMMA]] = LEMMA
                        self.words_count[self.words[LEMMA]] = 0

                    if self.words[LEMMA] not in self.context_words:
                        self.context_words[self.words[LEMMA]] = {}
                        self.context_words_dep[self.words[LEMMA]] = {}
                        self.context_words_two[self.words[LEMMA]] = {}
                        self.context_words_pmi[self.words[LEMMA]] = {}
                        self.context_words_dep_pmi[self.words[LEMMA]] = {}
                        self.context_words_two_pmi[self.words[LEMMA]] = {}

                    self.words_count[self.words[LEMMA]] += 1
                    sentence.append(self.words[LEMMA])
            else:
                if sentence != []:
                    sentences.append(sentence)
                    sentence = []
                if dependencies != []:
                    for vector in dependencies:
                        parent = dependencies[vector["HEAD"]]
                        if parent["POSTAG"] == "IN": #parent is preposition
                            parent_parent = dependencies[parent["HEAD"]]
                            # parent parent is to be connected to vector
                            feature_vector = (parent_parent["LEMMA"], parent["DEPREL"], "up")
                            feature_parent_parent = (vector["LEMMA"], parent["DEPREL"], "down")
                            if feature_vector not in self.features_dep:
                                self.features_dep[feature_vector] = len(self.features_dep)
                            if feature_parent_parent not in self.features_dep:
                                self.features_dep[feature_parent_parent] = len(self.features_dep)
                            deps.append(self.features_dep[feature_vector])
                            deps.append(self.features_dep[feature_parent_parent])
                    if deps != []:
                        all_deps.append(deps)
        self.words_count =  { id:count for id,count in self.words_count.iteritems() if count > THRESHOLD }
        for id, count in self.words_count.iteritems():
            total_count += count
        self.words = { word:id for word,id in self.words.iteritems() if id in self.words_count }
        self.words_to_ix = { id: word for word, id in self.words.iteritems() }
        self.features_dep_to_ix = { id: feature for feature, id in self.features_dep.iteritems() }
        sentences = [ [ word for word in sentence if word in self.words_to_ix ] for sentence in sentences ]
        print "finish reading the corpus " + str(passed_time(start_time))
        for i, sentence in enumerate(sentences):
            count = Counter(sentence)
            for k, id_word in enumerate(sentence):
                for j, (id_other, freq) in enumerate(count.iteritems()):
                    if freq > MIN_CO:
                        if id_other != id_word:
                            if id_other not in self.context_words[id_word]:
                                self.context_words[id_word][id_other] = freq
                            else:
                                self.context_words[id_word][id_other] += freq
                            if k < j + 2 and k > j - 2:
                                if id_other not in self.context_words_two[id_word]:
                                    self.context_words_two[id_word][id_other] = freq
                                else:
                                    self.context_words_two[id_word][id_other] += freq
        print "finish building the freqs " + str(passed_time(start_time))
        for id_word in self.words_to_ix:
            for id_cont, freq in self.context_words[id_word].iteritems():
                pmi = log( (float(freq) * total_count)/(float(self.words_count[id_cont]*self.words_count[id_word]) ) )
                if pmi < 0:
                    pmi = 0
                self.context_words_pmi[id_word][id_cont] = pmi
            for id_cont, freq in self.context_words_two[id_word].iteritems():
                pmi = log( (float(freq) * total_count)/(float(self.words_count[id_cont]*self.words_count[id_word]) ) )
                if pmi < 0:
                    pmi = 0
                self.context_words_two_pmi[id_word][id_cont] = pmi
        print "finish building the pmis " + str(passed_time(start_time))


if __name__ == '__main__':
    corpus = Corpus()
