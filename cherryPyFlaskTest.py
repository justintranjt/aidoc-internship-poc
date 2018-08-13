from flask import Flask
from cheroot import wsgi

app = Flask(__name__)
bind_addr = '0.0.0.0', 8080

@app.route("/")
def hello():
	return "TEST RESPONSE HERE"

if __name__ == "__main__":
	wsgi.Server(bind_addr, app).safe_start()
