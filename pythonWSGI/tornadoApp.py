from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.options import define, options

# Define options
define("port", default=8080, help="Run on the given port", type=int)

class HelloWorld(RequestHandler):
	def get(self):
		self.write("Hello, world")

def main():
	app = Application(
		[
			(r"/", HelloWorld),
		],
	)

	print('Listening on http://localhost:%i' % options.port)
	app.listen(options.port)
	IOLoop.current().start()

if __name__ == "__main__":
	main()
