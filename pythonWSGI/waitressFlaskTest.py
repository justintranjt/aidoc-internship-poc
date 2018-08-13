from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/")
def hello():
	return "loaderio-ef7ba94a3fa0cf401fd742775c6f8a38!"

if __name__ == "__main__":
	# Waitress serving app using 10 threads and asynchronous workers
	#app.run(host='0.0.0.0', port=8080)
	serve(app, host='0.0.0.0', port=8080, threads=10, asyncore_use_poll=True, asyncore_loop_timeout=10)
