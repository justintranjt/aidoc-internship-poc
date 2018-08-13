# Choosing the Perfect Python WSGI Server for Your Windows Environment in 2018

Another annoying aspect of working with tight restrictions due to HIPAA was the limited set of hardware that radiologists were able to work with. Nearly all the machines we developed for had to be Windows and as a result, building purely for Windows required using Windows-compatible tools at some points.

Therefore, choosing the correct Python WSGI server that could handle high loads was extremely important for the wellbeing of the application as Aidoc scaled to larger operations.

WSGI has two aspects. It is made to let web servers (such as Apache or Nginx) forward requests to web apps or frameworks written in Python.

* **Server/Gateway side:** Full web server or application that communicates with server
* **Application/Framework side:** Python callable supplied by program or framework

For example, a WSGI-compliant server such as Waitress or Gunicorn hosts a WSGI-compliant web app (such as Flask or Django).

![WSGI diagram]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/wsgiExplanation.png )*A WSGI server (meaning WSGI compliant) simply receives the request from the client, passes it to the application and then sends the response returned by the application to the client*

WSGI is built to be synchronous but some of the implementations we test have workarounds to this. Note that many WSGIs are placed behind a reverse proxy such as Apache or Nginx to use a HTTPS URL scheme or support a SSL connection.

The reverse proxy commonly handles static requests while passing off all other requests to the WSGI.

We chose between 5 different WSGI Servers compatible with Windows, of which only 3 were even acceptable as others had poor performance.

Our candidates were **Waitress, CherryPy, Twisted Web, mod_wsgi**, and **gevent** (the WSGI currently in use and the one we were hoping to replace as soon as possible).

3 forms of load-testing operations were tested against each of the servers. Each was administered using JMeter to create "threads" or "users" emulating actual traffic:
1. 1000 (linearly growing) users over 1 minute
2. 1000 immediate, concurrent users over 1 minute
3. 1000 immediate, concurrent users over 1 minute and maintained for another minute

Let's get right to the results measuring the percent error (percent of connections dropped):

        |             | Waitress | CherryPy | Twisted Web | mod_wsgi | gevent |
        |:-----------:|:--------:|:--------:|:-----------:|:--------:|:------:|
        | Test 1 Avg. |   0.00%  |   0.00%  |    0.00%    |   0.00%  |  0.00% |
        | Test 2 Avg. |  18.12%  |  17.71%  |    33.67%   |  34.89%  | 20.51% |
        | Test 3 Avg. |  30.87%  |  26.97%  |    52.02%   |  50.93%  | 51.37% |

Waitress and CherryPy are the best WSGI servers of choice for a modern Python WSGI server in need of speed and high load.

# Why are there any errors at all? Shouldn’t a WSGI be able to handle any load?

Even with stacktraces I was not able to pinpoint a direct cause of these errors though I did log and trace many of these errors to HTTP 502 errors to the server. The 502 Bad Gateway error likely resulted from WSGI workers trying to handle the requests only for some of the requests to time out resulting in errors. 

I have a theory that it is related to the standard I/O registry value in Windows that determines the number of open files at any time (limited to 512 by default). For more info, [view this page](https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/setmaxstdio).

Nonetheless, with the correct configurations from the possible configurations I listed for each WSGI in addition to the configured Nginx server ideal for our network settings, the tests are all standardized and Waitress and CherryPy would at the very least be able to handle the highest number of concurrent requests.

I also confirmed my suspicions about why there were so many errors from HTTP 503 error codes using each WSGI. It is a combination of Windows’ low open file limit and unconfigured server settings that would replicate a production setting. [Here is a Github comment](https://github.com/pallets/flask/issues/1073#issuecomment-44681572) about a similar issue. It shouldn’t be an issue in production especially by using better hardware with correctly configured threads.

**Conclusion:** CherryPy is the fastest and responded the best to handling high loads. 
Waitress was the simplest to use because of its lack of dependencies and close integration to Python but was slower. 
Twisted Web was difficult to work with as it has undergone heavy renaming and revamps through the last few years. It also performed staggeringly worse than the other WSGIs, having an average error rate of ~50% in test 3 when the others hovered ~30% or less. 
mod_wsgi is commonly found due to being one of the first production-ready WSGI servers and has a wealth of documentation over the years but is now outperformed by modern WSGIs. It is also tied heavily to Apache which is not as beneficial if our developers are already used to Nginx. The performance was quite disappointing as it was similar to Twisted Web and the installation process was slightly confusing coming from somebody that had never interacted with Apache before.
The best WSGIs were CherryPy and Waitress and while CherryPy handled high loads better, Waitress was easier to implement and configure (though they were both very easy to implement). CherryPy and Waitress configurations are simply arguments to the Server class and serve() function, respectively.

# Regarding Load-Testing on Windows
Note that every HTTP connection on a machine opens a new file descriptor. Windows sets a low limit for the maximum number of files that can be open and as a result, a limit less than the number of simulated users in a test will cause failures to occur before properly testing the actual load of the WSGI.

[This author also notes the same problem](http://blog.martinfjordvald.com/2011/04/optimizing-nginx-for-high-traffic-loads/) I addressed earlier with Windows and the open files limit. They write:

>“In case you hadn’t guessed it already then the odd one out is Windows. Nginx on Windows is really not an option for anything you’re going to put into production. Windows has a different way of handling event polling and the nginx author has chosen not to support this; as such it defaults back to using select() which isn’t overly efficient and your performance will suffer quite quickly as a result. 
>
>The second biggest limitation that most people run into is also related to your OS. Open up a shell, su to the user nginx runs as and then run the command `ulimit -a`. Those values are all limitations nginx cannot exceed. In many default systems the open files value is rather limited, on a system I just checked it was set to 1024. If nginx runs into a situation where it hits this limit it will log the error (24: Too many open files) and return an error to the client.”

# How do the WSGI servers work at the low-level?

## Waitress
* • Multi-threaded (rather than multi-processed using fork())
* • Synchronous (normal for WSGI) and asynchronous (not normal for WSGI) code is used

A channel is created for each client that connects to the WSGI server All requests with that client are made over the channel’s connection. When a channel receives a full HTTP request from the client, it schedules a task for the main thread to allocate. A main thread maintains a fixed pool of worker threads to handle tasks (parallelism). The default pool size is 4 by default.

If a worker thread is available, it will handle the task that was scheduled
When all worker threads are in use, a task will be buffered and wait in a queue for a worker thread to become available. The main thread is asynchronous while the workers are synchronous. Worker threads never perform I/O, it is only done by the main thread and many clients can be connected to the server at once because of this.
Worker threads will never be hung up trying to send data to a client with a slow network but with a maximum of 4 requests being handled at a time (by default).

## CherryPy
* • Multi-threaded (rather than multi-processed using fork())

The general idea behind threaded handling of requests is similar to Waitress with a few notable differences. 

The server maintains a single, main listening thread and places incoming connections from clients onto a queue. The main listening thread is not asynchronous as it was implemented before 2016 when Python 3.5 was released with async features
Worker threads are also kept in a fixed pool and handle tasks off the queue as they’re popped off.

## Gevent
* • Looks very much like traditional threaded programming, but underneath does asynchronous I/O
* • Uses greenlets

A “greenlet” is a small independent pseudo-thread. Think about it as a small stack of frames; the bottom frame is the initial function you called, and the topmost frame is the one in which the greenlet is currently paused. You work with greenlets by creating a number of such stacks and jumping execution between them. Greenlets will only yield to other greenlets with a user-implemented yield command whereas traditional threads will yield to other threads when decided by the OS.

**Event loop:**
An event loop is run by a special greenlet called the hub. Instead of blocking and waiting for socket operations to complete (polling), gevent arranges for the OS to deliver an event letting it know when, for example, data has arrived to be read from the socket. 
gevent can move on to running another greenlet, perhaps one that itself now has an event ready for it. This repeated process of registering for events and reacting to them as they arrive is the event loop.

Greenlets all run in the same thread. This means that until a particular greenlet gives up control, such as with the sleep() function, other greenlets won’t get a chance to run. In addition, only one greenlet runs at a time. Multiprocessing is known to cause problems with gevent’s use of monkey patching (reopening a class or method at runtime and changing its execution). Therefore, gevent takes advantage of concurrency by using context switching but not parallelism.
