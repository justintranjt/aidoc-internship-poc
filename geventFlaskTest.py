from flask import Flask
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

@app.route("/")
def hello():
	return "loaderio-ef7ba94a3fa0cf401fd742775c6f8a38!"

if __name__ == "__main__":
	# Disabled logging because it printed to the terminal, sucking up resources
	# I made sure the other tested WSGIs also did not print to terminal
	WSGIServer(('0.0.0.0', 8080), application=app, log=None, error_log=None).serve_forever()
