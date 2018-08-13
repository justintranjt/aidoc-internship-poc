from flask import Flask
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.server import Site

app = Flask(__name__)

@app.route("/")
def hello():
	return "Twisted Web and Flask test"

if __name__ == "__main__":
	# Set up a WSGI resource at /
	flask_site = WSGIResource(reactor, reactor.getThreadPool(), app)
	# Create website
	site = Site(flask_site)
	# Listen for site on port 8080
	reactor.listenTCP(8080, site)
	reactor.run()
