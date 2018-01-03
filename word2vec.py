import time
import numpy as np

WORDS = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar", "piano"]
start_time = time.time()

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

def load_and_normalize(words2vec):
    words = []
    w = []
    with open(words2vec, "r") as lines:
        for i, line in enumerate(lines):
            vector = line.split()
            word = vector.pop(0)
            words.append(word)
            word_vector = map(float, vector)
            w.append(word_vector / np.linalg.norm(word_vector))
    return np.asarray(w), np.asarray(words)

def calculate_similars(name_type):
    W, words = load_and_normalize(name_type + ".words")
    C, contexts = load_and_normalize(name_type+ ".contexts")
    print "finish loading " + str(passed_time(start_time))
    w2i = {w:i for i, w in enumerate(words)}
    c2i = {w:i for i, w in enumerate(contexts)}
    for word in WORDS:
        word_vector = W[w2i[word]]
        sims = np.dot(W, word_vector)
        most_similars_ids = sims.argsort()[-1:-22:-1]
        sim_words = words[most_similars_ids]
        print "~~~~~~~~~~~"
        print word
        print "___________"
        i = 0
        j = 0
        print "SECOND ORDER"
        while i < 20:
            if sim_words[j] != word:
                print sim_words[j] + ";" + str(sims[most_similars_ids[j]])
                i += 1
            j += 1
        # sims_2 = C.dot(word_vector)
        # most_similars_ids_2 = sims_2.argsort()[-1:-12:-1]
        # sim_words_2 = contexts[most_similars_ids_2]
        # i = 0
        # j = 0
        # print "FIRST ORDER"
        # while i < 10:
        #     if sim_words_2[j] != word:
        #         to_print = sim_words_2[j].split("_")
        #         if len(to_print) > 1:
        #             print str(to_print[1]) + ";" + str(sims_2[most_similars_ids_2[j]])
        #         else:
        #             print str(to_print[0]) + ";" + str(sims_2[most_similars_ids_2[j]])
        #
        #         i += 1
        #     j += 1
    print "finish calculate " + str(passed_time(start_time))


print "Window of 5"
print "========"
calculate_similars("bow5")

print "Dependencies"
print "========"
calculate_similars("deps")
