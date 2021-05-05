from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *

project_name = "Online Course Recommender"
net_id = "Brian Pukmel bp322, Ziwei Gu zg48, Matthew Hall-Pena mh2474"

initialize()

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	min_rating = request.args.get('rating')
	max_price = request.args.get('price')
	level = request.args.get('level')
	num_results = request.args.get('num_results')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Recommended courses for query \"" + query + "\""
		data = find_courses(query,query, float(min_rating), int(max_price), level, int(num_results))
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



