import csv
from nltk.tokenize import TreebankWordTokenizer
import numpy as np
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer 
#from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer,strip_accents_unicode
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter

#file1 = open('stopwords_eng.txt','r')

#stopwords = file1.read().splitlines()
#stopwords.words('english')


stopwords = ['i', 'me','my','myself','we','our','ours','ourselves','you',"you're","you've","you'll","you'd",'your','yours','yourself','yourselves','he','him',
 'his','himself','she',"she's",'her','hers','herself','it',"it's",'its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that',
 "that'll", 'these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a',
 'an','the','and','but','if','or', 'because', 'as','until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all','any','both','each','few','more','most',
 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
 "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn',
 "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',"isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]


class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, articles):
        return [self.wnl.lemmatize(t) for t in word_tokenize(articles) if t not in stopwords and t.isalnum()]


coursera_data = []
coursera_courses = {}
coursera_course_names = []
coursera_docs = None
tfidf= None
tfidf_vectorizer = None


def initialize():
	global coursera_data,coursera_courses,coursera_course_names,coursera_docs,tfidf,tfidf_vectorizer

	with open('coursera_data.csv') as f:
		coursera_data = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

	index = 0
	for i in coursera_data:
		if i["course_name"] not in coursera_courses:
			coursera_courses[i["course_name"]] = i
			coursera_courses[i["course_name"]]["id"] = index

			coursera_course_names.append(i["course_name"])
			index += 1

	tfidf_vectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), strip_accents = 'unicode',lowercase = True,max_df = 0.5,min_df = 1,use_idf=True)

	tfidf = tfidf_vectorizer.fit_transform([i.lower() for i in coursera_course_names]).toarray()

def find_courses(query, min_rating=1.0, level=None, num_results=10):
	a = tfidf_vectorizer.build_analyzer()
	query_tfidf = tfidf_vectorizer.transform([query])
	cosineSimilarities = cosine_similarity(query_tfidf, tfidf).flatten()
	
	sorted_docs = cosineSimilarities.argsort()[::-1]
	results = []

	for i in sorted_docs:
		name = coursera_course_names[i]
		if (coursera_courses[name]["course_rating"] == "None" or float(coursera_courses[name]["course_rating"]) >= min_rating) and (coursera_courses[name]["course_level"] == "None" or level == None or coursera_courses[name]["course_level"] == level):
			results.append(coursera_courses[name])
			num_results -= 1
		if num_results == 0:
			break

	return sorted(results, key=itemgetter('course_rating'), reverse=True)
