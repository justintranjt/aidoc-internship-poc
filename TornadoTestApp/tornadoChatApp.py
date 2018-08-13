# AJAX chat room using Tornado async functions

import os.path
# coordinate Tornado coroutines in a single-threaded app
import asyncio
from tornado.escape import to_unicode
from tornado.locks import Condition
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import RequestHandler, Application
import uuid  # Unique IDs

# Define options
define("port", default=8080, help="Run on the given port", type=int)
define("debug", default=True, help="Running in debug mode")

# Holds total buffer of all chat messages
class MessageBuffer(object):
    def __init__(self):
        self.cond = Condition()
        self.cache = []  # all messages added here
        self.cache_size = 200  # holds 200 newest msgs

    # return all messages since message with id=lastID
    def get_messages_since(self, lastID):
        results = []
        for msg in reversed(self.cache):
            if msg['id'] == lastID:
                break  # stop once you get here
            results.append(msg)
        results.reverse()
        return results

    # add msg to cache
    def add_message(self, message):
        self.cache.append(message)  # add msg
        if len(self.cache) > self.cache_size:  # change out old msgs
            self.cache = self.cache[-self.cache_size:]
        self.cond.notify_all()  # notify all coroutines aka all connected users


# Create a buffer for use by individual msgs to add to
global_message_buffer = MessageBuffer()

# Main function of app
class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html", messages=global_message_buffer.cache)

# Post new message to chat room
class NewMessageHandler(RequestHandler):
    def post(self):
        message = {
            'id': str(uuid.uuid4()),  # generate unique ID for this message
            # returns value of 'body' argument
            'body': self.get_argument('body')
        }

        # Message to be rendered with message.html, must convert to char string
        message['html'] = to_unicode(self.render_string(
            "message.html", message=message))
        if self.get_argument('next', None):  # If no message body, error
            self.redirect(self.get_argument('next'))
        else:
            self.write(message)

        global_message_buffer.add_message(
            message)  # Add message to global buffer


# Async function, long polling request for new messages
# Waits until new messages are available before returning
class UpdatesMessageHandler(RequestHandler):
    async def post(self):
        lastID = self.get_argument('lastID', None)
        messages = global_message_buffer.get_messages_since(lastID)

        while not messages:
            self.wait_future = global_message_buffer.cond.wait()
            try:  # wait for future
                await self.wait_future
            except asyncio.CancelledError:  # Future was cancelled
                return
            messages = global_message_buffer.get_messages_since(lastID)

        # if connection is already closed just cancel
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))  # update displayed messages

    def on_connection_close(self):
        self.wait_future.cancel()


def main():
    parse_command_line()  # All options passed in through command line
    # define application with the options defined
    app = Application(
        [
            (r"/", MainHandler),
            (r"/a/message/new", NewMessageHandler),
            (r"/a/message/updates", UpdatesMessageHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug
    )
    app.listen(options.port)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
