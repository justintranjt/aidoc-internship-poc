from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
	return "loaderio-ef7ba94a3fa0cf401fd742775c6f8a38!"

if __name__ == "__main__":
	app.run()
