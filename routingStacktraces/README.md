# Routing Sensitive Stacktraces Through HIPAA-Regulated Networks

We also host an Electron app that is installed on the computers of radiologists inside hospital networks. Of course, we had to handle similar crash data using Sentry.io. The twist here was having to use our own secure server approved by HIPAA regulations that could take any crash data from the Electron app and act as a reverse proxy to send the data to Sentry.io.

**Objective:** Configure an HTTPS route to a local Nginx server which will then send a query to Sentry.io. To do this we would need to create a self-signed SSL certificate. Configure the Electron app's Sentry's SDK to send data to this HTTPS port. Essentially, we are routing all crash data from the Electron app through a HTTPS Nginx server before using the server as a reverse proxy to send the data to the Sentry platform. This is required due to the limitations of the hospital network that only allow access to a virtual machine and no other internet access.

The following are a few of the important files vital to the process:

**Electron:**
`Main.js` (contains basic Electron app structure)

**Nginx:**
`Nginx.conf` (contains server configuration and HTTP to HTTPS redirection)
`Access.log` (log of all data to and from server)

**Sentry:**
`Sentry.js` (contains DSN)

Our DSN is in the form `https://[PUBLIC_KEY]@[HOST]/[PROJECT_ID]`. The important aspect of this is that the host is sentry.io. Clearly we can’t use this configuration for our architecture where the hospital and its Electron app does not have access to the internet. So, we must route it through our localhost server running Nginx instead:

![sentryDSN]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/sentryDSN.PNG )*My unique Sentry.io DSN*

Note that our Nginx server must be started to begin this. Also note that we changed the host to be `localhost` (our Nginx server) and that the DSN is still HTTPS. Unfortunately, it turns out that Raven does not appreciate that our server uses a self-signed certificate. Raven throws an exception and our crash data fails to be routed through Nginx.

![SSL Error]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/sslError.PNG )*Nginx doesn't play well with self-signed certificates, even if they're for testing purposes*

**Possible Solution/Shortcomings:**
Seemingly the only way around this error is to send the DSN without HTTPS and with HTTP instead. Everything works perfectly when the crash data is routed from Electron to our HTTP configured server and finally to the Sentry server (which is HTTPS) but this is obviously not secure. An alternative solution is to let our Nginx server config handle the redirection from HTTP to HTTPS instead (note that this works but is not secure)

**Alternative Nginx.conf description:**
Lines 17-30 contain the server configuration that can be accessed through localhost or `http://localhost`. This does not utilize any certificate and is therefore unsecure. This is why line 23 redirects all requests to `http://localhost` to `https://localhost` which is secured with a self-signed certificate. We want our data to be secure when making requests to and from the Nginx server which is why we use SSL or TLS.

**Lines 25-29** contain the proxy that takes the data sent from the Electron app crash and Sentry’s Raven client (which handles and reports all crash data in a form that can be read by Sentry). The location directive contains a regular expression that handles data sent from Raven in the query form: …/api/PROJECTID/store. This code was provided by a developer on the Sentry forum.

**Lines 33-65** contain the HTTPS configuration for our server. It is self-signed with an SSL certificate as seen in lines 37-41 and also password protected by a simple test username and password as seen in lines 43-45. Links to webpages and access to images stored in the server’s root are provided by location directives in lines 47-59.

**Lines 52-53** were used for testing the sending of HTTP requests to the server. Nginx servers hosting static pages do not allow POST requests (HTTP code 405) so a workaround was made in which GET requests with a request_body were sent to the server instead and 405 errors were converted to HTTP code 200 (success). This was all logged in access.log to ensure that HTTP requests and data sent to and from the server was making its way through Nginx effectively 

NOW, our solution hinges on **line 23** being either HTTP or HTTPS:
This redirection works perfectly when simply querying the server for example at http://localhost and visiting the static webpage. However, this does not work when redirecting the DSN from Raven. Instead, we receive an error like so:

![Redirecting data from HTTP to HTTPS]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/errorLikeSo.png )*The DSN cannot be routed from HTTP to HTTPS through Nginx and eventually to the Sentry platform because of an undefined error.*

The DSN cannot be routed from HTTP to HTTPS through Nginx and eventually to the Sentry platform because of an undefined error. It must solely be through HTTP because Sentry does not want unsecured data anywhere during data transfer. Unfortunately we had to stick to this HTTP solution.
