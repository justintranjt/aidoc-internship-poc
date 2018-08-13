/* Initialize Sentry SDK with assigned DSN immediately */
const { init } = require('@sentry/electron');
init({
  /* Replaced sentry.io DSN with DSN to our server which will route to Sentry.
     Actual server with HTTPS is hopefully signed otherwise it'll have to be 
     HTTP */
  // dsn: 'https://e84dcc8eee834e6f9dd81daddf757de1@sentry.io/1231686',

  // DSN to Nginx server. Note it is HTTP at the moment. Throws exception when
  // accessing through HTTPS
  dsn: 'http://e84dcc8eee834e6f9dd81daddf757de1@localhost/1231686',
});
