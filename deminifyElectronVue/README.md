# De-Minifying JavaScript with Source Maps in Electron-Vue Applications

An important part of Aidoc's product is an application shipped to radiologists for use in their PACS setup. This application is written with [electron-vue](https://github.com/SimulatedGREG/electron-vue). Of course, when the application crashed or threw a nasty exception, we would have to discover its origins with an in-depth stacktrace using a service such as [Sentry.io](https://sentry.io).

However, Sentry doesn't play well with minified JavaScript code (which electron-vue serves up in its builds) and stacktraces become practically indecipherable.

Objective: Create a test electron-vue project and build a simple app that crashes and routes its crash data and stacktrace to Sentry.io. Note that all electron-vue files are packaged with electron-builder and minified with Babili upon compilation. Our goal is to generate a sourcemap using Webpack that can provide a full stacktrace to Sentry.io. The following solutions assume you follow the [Sentry docs regarding source maps](https://docs.sentry.io/clients/javascript/sourcemaps/).

The bundled and minified code is found in `[app_root_folder]/dist/electron`. All the Webpack configuration specifying settings are found in `[app_root_folder]/electron-vue` in the 3 webpack configuration files:

`webpack.main.config.js`

`webpack.renderer.config.js`

`webpack.web.config.js`

We'll be working with webpack.main.config.js for the purposes of this solution.

Importantly, Webpack is able to generate a source map during minification through the use of the `devtool` field. BUT none are generated for some reason which is the root of the problem. 
This important field's documentation can be found here. It's also specified in the Sentry docs as being a way to create source maps. While this file has no devtool field, `webpack.renderer.config.js` and `webpack.web.config.js` contain `cheap-module-eval-source-map` as the style of source mapping (note that those files don't generate a map either).

I found that changing the `devtool` field to a different mapping (we have 12 to choose from) was able to generate `.js.map` files in some cases. It turns out that the Babili-Webpack plugin is [bugged](https://github.com/webpack-contrib/babel-minify-webpack-plugin/issues/68) and can't generate some source map styles in its current version. 

Add `"webpack-sources": "1.0.1"` to the `devDependencies` field in `package.json`.

```js
const SentryWebpackPlugin = require('@sentry/webpack-plugin');

let mainConfig = {
  devtool: 'source-map',
  // other configuration
  plugins: [
    new SentryWebpackPlugin({
      release: 'release: 'process.env.NODE_ENV',
      include: './dist',
      ignoreFile: '.sentrycliignore',
      ignore: ['node_modules', 'webpack.config.js'],
      configFile: 'sentry.properties'
    })
  ]
};
```

Like so: ![Working Webpack config]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/likeSo.png )*A working Sentry-Webpack configuration*

Remember to include with **source-map**. It is one one of the few source map styles that work with the bugged Babili-Webpack plugin.

This successfully generates a source map alongside the minified file. Right now, the minified file does not upload to Sentry successfully.

It looks like the map files are correctly uploading now. To get them to automatically upload, you must use the sentry-cli program with the command: `sentry-cli login`. If you can't access sentry-cli, it is found in `[app_root_folder]/node_modules/.bin`. 

You will login and copy and paste the auth token from the browser window that opens. Enter it and a .sentryclirc will be created in your application's root folder. It is now ready to ship source maps automatically now. Below I verified that they did upload automatically in the Releases -> Artifacts section.

![.map artifacts]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/artifacts.PNG )*.js and .js.map artifacts*

However, the .js.map and .map files still don't show correctly on the Issues page and it looks as though others have run into similar problems before with different source map styles: 

![Sentry doesn't like our map file]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/sentryMap.png )*Sentry refuses to use the source map we generated*

Use this small program that reads your source map file and tests a mapping (remember to install `source-map` through `npm` first):

```js
var fs        = require('fs'),
    path      = require('path'),
    sourceMap = require('source-map');

// file output by Webpack, Uglify, etc.
var GENERATED_FILE = path.join('.', '[YOUR_MAP_FILE_HERE]');

// line and column located in your generated file (e.g. source of your error
// from your minified file)
var GENERATED_LINE_AND_COLUMN = {line: 1, column: 1000};

var rawSourceMap = fs.readFileSync(GENERATED_FILE).toString();
var smc = new sourceMap.SourceMapConsumer(rawSourceMap);

var pos = smc.originalPositionFor(GENERATED_LINE_AND_COLUMN);

// should see something like:
// { source: 'original.js', line: 57, column: 9, name: 'myfunc' }
console.log(pos);
```
Despite our intense debugging and a properly uploaded source map, we Sentry.io refused to automatically use our source map. We have reached out to Sentry Support with no response at this point. For now, we are leaving our files bundled but unminified and using those stacktraces until we can find a better solution.
