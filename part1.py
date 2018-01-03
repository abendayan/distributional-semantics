import sys
import time
from math import sqrt, log
from collections import defaultdict, Counter
# WORDS = ["car", "piano"]
WORDS = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar", "piano"]
CONTENT_CLASSES = ['JJ','JJR','JJS','NN','NNS','NNP','NNPS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ','WRB']
PATH_FILE = "wikipedia.sample.trees.lemmatized"
start_time = time.time()
THRESHOLD = 100
SIMILAR = 20
MIN_CO = 1

FIRST_SECOND = int(sys.argv[2])

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

class Corpus:
    def __init__(self, type):
        self.type = type
        if self.type == 1:
            self.context_words = {}
            self.context_words_pmi = {}
        elif self.type == 2:
            self.context_words_two = {}
            self.context_words_two_pmi = {}
        elif self.type == 3:
            self.context_words_dep = {}
            self.context_words_dep_pmi = {}
            self.features = {}
            self.deprels = {}
            self.deprels_to_ix = {}
            self.feats_count = {}
        self.words = {}
        self.words_to_ix = {  }
        self.words_count = {}

        self.define_data()
        print "read all of the data " + str(passed_time(start_time))
        if self.type == 1:
            self.find_similar_words_in_sentence()
            print "found similar words in sentence " + str(passed_time(start_time))
        elif self.type == 2:
            self.find_similar_words_in_window()
            print "found similar words in window " + str(passed_time(start_time))
        elif self.type == 3:
            self.find_similar_words_deps()
            print "found similar words by deps " + str(passed_time(start_time))

    def find_similar_words_in_sentence(self):
        print "================ TYPE 1 ================"
        self.helper_find(self.context_words_pmi, self.words_to_ix)

    def find_similar_words_in_window(self):
        print "================ TYPE 2 ================"
        self.helper_find(self.context_words_two_pmi, self.words_to_ix)

    def find_similar_words_deps(self):
        print "================ TYPE 3 ================"
        self.helper_find(self.context_words_dep_pmi, self.words_to_ix, self.feature_to_word)

    def helper_find(self, dictionnary, to_ix, special = None):
        for test_word in WORDS:
            id_word = self.words[test_word]
            print test_word
            print "___________"
            count_word = dictionnary[id_word]
            close_words = []
            if self.type == 3:
                close_words_deps = [""] * SIMILAR
            if FIRST_SECOND == 1:
                for id_target, pmi in count_word.iteritems():
                    if special is not None:
                        targ = special(id_target)
                    else:
                        targ = id_target
                    if targ != id_word:
                        found = False
                        j = 0
                        while j < SIMILAR and not found:
                            if len(close_words) < SIMILAR:
                                j = len(close_words)
                                close_words.append((targ, pmi))
                                if self.type == 3:
                                    close_words_deps[j] = self.deprels_to_ix[id_target[1]]
                                found = True
                            elif close_words[j][1] < pmi:
                                close_words[j] = (targ, pmi)
                                if self.type == 3:
                                    close_words_deps[j] = self.deprels_to_ix[id_target[1]]
                                found = True
                            elif close_words[j][1] == pmi and close_words[j][0] == targ and self.type == 3:
                                close_words_deps[j] += "," + self.deprels_to_ix[id_target[1]]
                                found = True
                            j += 1
            if FIRST_SECOND == 2:
                DT = self.dot_product(id_word, count_word, dictionnary, special)
                for id_target, pmi in count_word.iteritems():
                    if special is not None:
                        targ = special(id_target)
                    else:
                        targ = id_target
                    if targ != id_word:
                        dist_word = DT[targ] / (sqrt(self.sum_square(id_word, dictionnary) * self.sum_square(targ, dictionnary)))
                        found = False
                        j = 0
                        while j < SIMILAR and not found:
                            if len(close_words) < SIMILAR:
                                if self.type == 3:
                                    while j < len(close_words):
                                        if close_words[j][1] == dist_word and close_words[j][0] == targ:
                                            close_words_deps[j] += "," + self.deprels_to_ix[id_target[1]]
                                            found = True
                                            j = len(close_words)
                                        else:
                                            j += 1
                                if not found:
                                    j = len(close_words)
                                    close_words.append((targ, dist_word))
                                    if self.type == 3:
                                        close_words_deps[j] = self.deprels_to_ix[id_target[1]]
                                    found = True
                            elif close_words[j][1] < dist_word:
                                close_words[j] = (targ, dist_word)
                                if self.type == 3:
                                    close_words_deps[j] = self.deprels_to_ix[id_target[1]]
                                found = True
                            elif close_words[j][1] == dist_word and close_words[j][0] == targ and self.type == 3:
                                close_words_deps[j] += "," + self.deprels_to_ix[id_target[1]]
                                found = True
                            j += 1

            for i, (temp_word, dist) in enumerate(close_words):
                if self.type != 3:
                    print to_ix[temp_word]
                else:
                    print to_ix[temp_word] + "[" + close_words_deps[i] +"]"
            print "================="

    def sum_square(self, id_word, dictionnary):
        count_word = dictionnary[id_word]
        total = 0.0
        for id, pmi in count_word.iteritems():
            total += pmi ** 2
        return total

    def feature_to_word(self, feature):
        word = feature[0]
        return word

    def dot_product(self, id_word, count_word, dictionnary, special = None):
        DT = {}
        for att_id, att_pmi in count_word.iteritems():
            if special is not None:
                word_id = special(att_id)
            else:
                word_id = att_id
            for v_id, v_pmi in dictionnary[word_id].iteritems():
                if special is not None:
                    v_id_feat = special(v_id)
                else:
                    v_id_feat = v_id
                if v_id not in DT:
                    DT[v_id_feat] = 0.0
                DT[word_id] = DT[v_id_feat] + att_pmi*v_pmi
        return DT

    def define_data(self):
        start_time = time.time()
        sentences = []
        sentence = []
        dependencies = []
        two_words_windows = []
        all_deps = []
        deps = []
        total_count = 0.0
        with open(PATH_FILE, "r") as words:
            for word in words:
                if word != "" and len(word) > 2:
                    ID, FORM, LEMMA, CPOSTAG, POSTAG, FEATS, HEAD, DEPREL, PHEAD, PDEPREL = word.split()
                    if self.type == 3:
                        # if POSTAG in CONTENT_CLASSES_DEP:
                        vector = {
                        "ID":ID,
                        "LEMMA":LEMMA,
                        "POSTAG":POSTAG,
                        "HEAD":int(HEAD),
                        "DEPREL":DEPREL,
                        }
                        dependencies.append(vector)
                        if DEPREL not in self.deprels:
                            self.deprels[DEPREL] = len(self.deprels)
                            self.deprels_to_ix[self.deprels[DEPREL]] = DEPREL
                    if POSTAG in CONTENT_CLASSES:
                        if LEMMA not in self.words:
                            self.words[LEMMA] = len(self.words)
                            # self.words_to_ix[self.words[LEMMA]] = LEMMA
                            self.words_count[self.words[LEMMA]] = 0
                        if self.type == 1:
                            if self.words[LEMMA] not in self.context_words:
                                self.context_words[self.words[LEMMA]] = {}
                                self.context_words_pmi[self.words[LEMMA]] = {}
                        elif self.type == 2:
                            if self.words[LEMMA] not in self.context_words_two:
                                self.context_words_two[self.words[LEMMA]] = {}
                                self.context_words_two_pmi[self.words[LEMMA]] = {}

                        self.words_count[self.words[LEMMA]] += 1
                        if self.type != 3:
                            sentence.append(self.words[LEMMA])
                else:
                    if self.type == 1 or self.type == 2:
                        if sentence != []:
                            sentences.append(sentence)
                            sentence = []
                    elif self.type == 3:
                        for vector in dependencies:
                            if vector["POSTAG"] in CONTENT_CLASSES:
                                parent = dependencies[vector["HEAD"] - 1]
                                if parent["POSTAG"] in CONTENT_CLASSES:
                                    id_vector = self.words[vector["LEMMA"]]
                                    id_parent = self.words[parent["LEMMA"]]
                                    feature_parent = (id_parent, self.deprels[parent["DEPREL"]], "up")
                                    feature_vector = (id_vector, self.deprels[parent["DEPREL"]], "down")
                                    if id_vector not in self.context_words_dep:
                                        self.context_words_dep[id_vector] = {}
                                    if feature_parent not in self.context_words_dep[id_vector]:
                                        self.context_words_dep[id_vector][feature_parent] = 0
                                    self.context_words_dep[id_vector][feature_parent] += 1

                                    if id_parent not in self.context_words_dep:
                                        self.context_words_dep[id_parent] = {}
                                    if feature_vector not in self.context_words_dep[id_parent]:
                                        self.context_words_dep[id_parent][feature_vector] = 0
                                    self.context_words_dep[id_parent][feature_vector] += 1
                                    if feature_parent not in self.feats_count:
                                        self.feats_count[feature_parent] = 0
                                    if feature_vector not in self.feats_count:
                                        self.feats_count[feature_vector] = 0
                                    self.feats_count[feature_parent] += 1
                                    self.feats_count[feature_vector] += 1
                                if parent["POSTAG"] is "IN":
                                    parent_parent = dependencies[parent["HEAD"] - 1]
                                    if parent_parent["POSTAG"] in CONTENT_CLASSES:
                                        id_vector = self.words[vector["LEMMA"]]
                                        id_parent = self.words[parent_parent["LEMMA"]]
                                        feature_parent = (id_parent, self.deprels[parent_parent["DEPREL"]], "up")
                                        feature_vector = (id_vector, self.deprels[parent_parent["DEPREL"]], "down")
                                        if id_vector not in self.context_words_dep:
                                            self.context_words_dep[id_vector] = {}
                                        if feature_parent not in self.context_words_dep[id_vector]:
                                            self.context_words_dep[id_vector][feature_parent] = 0
                                        self.context_words_dep[id_vector][feature_parent] += 1

                                        if id_parent not in self.context_words_dep:
                                            self.context_words_dep[id_parent] = {}
                                        if feature_vector not in self.context_words_dep[id_parent]:
                                            self.context_words_dep[id_parent][feature_vector] = 0
                                        self.context_words_dep[id_parent][feature_vector] += 1
                                        if feature_parent not in self.feats_count:
                                            self.feats_count[feature_parent] = 0
                                        if feature_vector not in self.feats_count:
                                            self.feats_count[feature_vector] = 0
                                        self.feats_count[feature_parent] += 1
                                        self.feats_count[feature_vector] += 1
                        dependencies = []
        if self.type != 3:
            self.words_count =  { id:count for id,count in self.words_count.iteritems() if count > THRESHOLD }
        for id, count in self.words_count.iteritems():
            total_count += count
        self.words = { word:id for word,id in self.words.iteritems() if id in self.words_count }
        self.words_to_ix = { id: word for word, id in self.words.iteritems() }
        if self.type != 3:
            sentences = [ [ word for word in sentence if word in self.words_to_ix ] for sentence in sentences ]
        print "finish reading the corpus " + str(passed_time(start_time))

        if self.type == 1:
            for i, sentence in enumerate(sentences):
                count = Counter(sentence)
                for k, id_word in enumerate(sentence):
                    for j, (id_other, freq) in enumerate(count.iteritems()):
                        if id_other != id_word:
                            if id_other not in self.context_words[id_word]:
                                self.context_words[id_word][id_other] = freq
                            else:
                                self.context_words[id_word][id_other] += freq

            self.context_words = { id_word :  {  id_other:freq for id_other, freq in dict_other.iteritems() if freq > MIN_CO }   for id_word, dict_other in self.context_words.iteritems()  }
            print "finish building the freqs for sequences " + str(passed_time(start_time))

        elif self.type == 2:
            for i, sentence in enumerate(sentences):
                count = Counter(sentence)
                for k, id_word in enumerate(sentence):
                    for j, (id_other, freq) in enumerate(count.iteritems()):
                        if id_other != id_word:
                            if k < j + 2 and k > j - 2:
                                if id_other not in self.context_words_two[id_word]:
                                    self.context_words_two[id_word][id_other] = freq
                                else:
                                    self.context_words_two[id_word][id_other] += freq
            self.context_words_two = { id_word :  {  id_other:freq for id_other, freq in dict_other.iteritems() if freq > MIN_CO }   for id_word, dict_other in self.context_words_two.iteritems()  }
            print "finish building the freqs for window 2 " + str(passed_time(start_time))
        elif self.type == 3:
            self.context_words_dep = { id_word :  {  id_other:freq for id_other, freq in dict_other.iteritems() if freq > MIN_CO }   for id_word, dict_other in self.context_words_dep.iteritems()  }

        if self.type == 1:
            for id_word in self.words_to_ix:
                for id_cont, freq in self.context_words[id_word].iteritems():
                    pmi = log( float(freq)*total_count/(float(self.words_count[id_cont]*self.words_count[id_word]) ) )
                    if pmi < 0:
                        pmi = 0
                    self.context_words_pmi[id_word][id_cont] = pmi
            print "finish building the pmis for sequences " + str(passed_time(start_time))
        elif self.type == 2:
            for id_word in self.words_to_ix:
                for id_cont, freq in self.context_words_two[id_word].iteritems():
                    pmi = log( float(freq)*total_count/(float(self.words_count[id_cont]*self.words_count[id_word]) ) )
                    if pmi < 0:
                        pmi = 0
                    self.context_words_two_pmi[id_word][id_cont] = pmi
            print "finish building the pmis for 2 window" + str(passed_time(start_time))
        elif self.type == 3:
            for id_word in self.words_to_ix:
                if id_word in self.context_words_dep:
                    for feature, freq in self.context_words_dep[id_word].iteritems():
                        if freq > 0:
                            pmi = log( (float(freq) * total_count) / (float(self.words_count[id_word] * self.feats_count[feature])   )  )
                            # if pmi < 0:
                            #     pmi = 0
                            if pmi > 0:
                                if id_word not in self.context_words_dep_pmi:
                                    self.context_words_dep_pmi[id_word] = {}
                                self.context_words_dep_pmi[id_word][feature] = pmi

            print "finish building the pmis " + str(passed_time(start_time))


if __name__ == '__main__':
    type = int(sys.argv[1])
    sequence = Corpus(type)
    # del sequence
    # windows = Corpus(2)
    # del windows
    # dependencies = Corpus(3)
