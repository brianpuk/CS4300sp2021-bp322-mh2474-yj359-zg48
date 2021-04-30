from csv import DictReader
from nltk.tokenize import TreebankWordTokenizer
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
#from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer,strip_accents_unicode
from sklearn.metrics.pairwise import cosine_similarity
#import sys
#import resource

stopwords = stopwords.words('english')


class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, articles):
        return [self.wnl.lemmatize(t) for t in word_tokenize(articles) if t not in stopwords and t.isalnum()]


courses = {}
course_names = []
data = []
docs = None
tfidf_names= None
tfidf_tags= None
tfidf_vectorizer_names = None
tfidf_vectorizer_tags = None


def initialize():
	global data,courses,course_names,docs,tfidf_names,tfidf_tags,tfidf_vectorizer_names,tfidf_vectorizer_tags

	length = 114579
	pieces = 3
	start = 0
	index = 0
	num = 0
	with open('../../../udemy_coursera_edx.csv') as f:
		for row in DictReader(f, skipinitialspace=True):
			if length/pieces * (num + 1) >= index:
				data.append({k: v for k, v in row.items()})
			else:
				start = proccess(start)
				num += 1
				data.append({k: v for k, v in row.items()})
			index += 1
		proccess(start)

	for i in courses:
		del courses[i]["user_rating"]
		del courses[i]["review"]

	#tfidf_vectorizer_names = TfidfVectorizer(tokenizer=LemmaTokenizer(), strip_accents = 'unicode',lowercase = True,max_df = 0.1,min_df = 15,use_idf=True)
	#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))
	tfidf_vectorizer_tags = TfidfVectorizer(tokenizer=LemmaTokenizer(), strip_accents = 'unicode',lowercase = True,max_df = 0.3,min_df = 10,use_idf=True)
	#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))

	#tfidf_names = tfidf_vectorizer_names.fit_transform([i.lower() for i in course_names]).toarray()
	tfidf_tags = tfidf_vectorizer_tags.fit_transform([courses[i]["tags"].lower() for i in course_names]).toarray()
	#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))
	#print(courses[course_names[0]])
	'''print(len(tfidf_names))
	print(len(tfidf_names[0]))
	print(sys.getsizeof(tfidf_names))
	print()
	print(len(tfidf_tags))
	print(len(tfidf_tags[0]))
	print(sys.getsizeof(tfidf_tags))
	print()
	print(sys.getsizeof(tfidf_vectorizer_names))
	print(sys.getsizeof(tfidf_vectorizer_tags))
	print(sys.getsizeof(courses))'''

def proccess(start):
	global data,courses,course_names,docs,tfidf_names,tfidf_tags,tfidf_vectorizer_names,tfidf_vectorizer_tags
	#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))

	#sentiment = SentimentIntensityAnalyzer()
	index = start
	for i in data:
		if i["course_name"] not in courses:
			courses[i["course_name"]] = i
			courses[i["course_name"]]["id"] = index
			courses[i["course_name"]]["tags"] = "".join(courses[i["course_name"]]["tags"])

			course_names.append(i["course_name"])
			index += 1
		elif i["link"] != courses[i["course_name"]]["link"]:
			if  "coursera" in courses[i["course_name"]]["link"] and ("edx" in i["link"] or "udemy" in i["link"]):
				i["course_name"] = i["course_name"] + " Coursera"
				if i["course_name"] not in courses: 
					courses[i["course_name"]] = i
					courses[i["course_name"]]["id"] = index
					courses[i["course_name"]]["tags"] = "".join(courses[i["course_name"]]["tags"])

					course_names.append(i["course_name"])
					index += 1
			'''elif i["course_partner"] != "" and i["course_partner"] != courses[i["course_name"]]["course_partner"]:
				i["course_name"] = i["course_name"] + " " + i["course_partner"]
				if i["course_name"] not in courses: 
					courses[i["course_name"]] = i
					courses[i["course_name"]]["id"] = index
					courses[i["course_name"]]["tags"] = "".join(courses[i["course_name"]]["tags"])

					course_names.append(i["course_name"])
					index += 1'''
			#else:
				#print(i["course_name"])
				#print(i["link"],courses[i["course_name"]]["link"])
		else:
			current = 0
			if courses[i["course_name"]]["course_enrollments"] != "":
				current = float(courses[i["course_name"]]["course_enrollments"])
			#courses[i["course_name"]]["course_enrollments"] = str(current + 300*sentiment.polarity_scores(i["review"])["compound"])
	
	#print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**10))
	data = []
	return index

def find_courses(query_names=None, query_tags=None, min_rating=1.0, max_price=None, level=None, num_results=10):
	scores = None

	if query_names != None:
		a = tfidf_vectorizer_names.build_analyzer()
		query_name_tfidf = tfidf_vectorizer_names.transform([query_names])
		cosine_similarities_names = cosine_similarity(query_name_tfidf, tfidf_names).flatten()

		if query_tags == None:
			scores = cosine_similarities_names
		else:
			b = tfidf_vectorizer_tags.build_analyzer()
			query_tags_tfidf = tfidf_vectorizer_tags.transform([query_tags])
			cosine_similarities_tags = cosine_similarity(query_tags_tfidf, tfidf_tags).flatten()

			scores = cosine_similarities_tags + cosine_similarities_names * 2
	elif query_tags != None:
		b = tfidf_vectorizer_tags.build_analyzer()
		query_tags_tfidf = tfidf_vectorizer_tags.transform([query_tags])
		cosine_similarities_tags = cosine_similarity(query_tags_tfidf, tfidf_tags).flatten()

		scores = cosine_similarities_tags
	else:
		return None


	for i in range(len(course_names)):
		if courses[course_names[i]]["course_rating"] != "none" and courses[course_names[i]]["course_rating"] != "":
			scores[i] *= float(courses[course_names[i]]["course_rating"])
		else:
			scores[i] *= 4 #Placeholder

	sorted_docs = scores.argsort()[::-1]
	results = []


	best_score = scores[sorted_docs[0]]
	for i in sorted_docs:
		name = course_names[i]
		if num_results <= 0:
			if scores[i] < .8 * best_score: #Placeholder
				break
		if (courses[name]["course_rating"] == "none" or courses[name]["course_rating"] == "" or float(courses[name]["course_rating"]) >= min_rating) and (courses[name]["course_level"] == "none" or courses[name]["course_level"] == "" or level == None or courses[name]["course_level"] == level) and (courses[name]["price"] == "" or max_price == None or float(courses[name]["price"])  <= max_price):
			results.append(courses[name])
			num_results -= 1

	while num_results < 0:
		min_enrollment = -1
		for i in results:
			if i["course_enrollments"] == "":
				i["course_enrollments"] = "0"
			if min_enrollment == -1 or float(i["course_enrollments"]) < min_enrollment:
				min_enrollment = float(i["course_enrollments"])

		for i in reversed(range(len(results))):
			if float(results[i]["course_enrollments"]) == min_enrollment:
				del results[i]
				num_results += 1
				break

	return results

'''
from memory_profiler import memory_usage

def myfunc():
  # code
  initialize(114579,3)
  return

mem = max(memory_usage(proc=myfunc))

print("Maximum memory used: {} MiB".format(mem))
'''
initialize()