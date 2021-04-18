import csv
from nltk.tokenize import TreebankWordTokenizer
import numpy as np
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer,strip_accents_unicode
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter

stopwords = stopwords.words('english')

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

	with open('../coursera_data.csv') as f:
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

def search(query, min_rating=1.0, level=None, num_results=10):
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
