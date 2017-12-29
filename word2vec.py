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
