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
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Recommended courses for query \"" + query + "\""
		data = find_courses(query,query)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



