const electron = require('electron')
const {ipcMain} = require('electron')
var path = require('path')

/* Active Sentry Electron process early. Supports errors in renderer processes*/
require('./sentry')

// Module to control application life.
const app = electron.app
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

// Open a second window from the main process when something was done from the 
// renderer process (button clicked)
let secondWindow

function createWindow() {
    // Create the browser window.
    mainWindow = new BrowserWindow({
    	frame: false, // Hide title bar
        titleBarStyle: 'hidden',
        width: 1281,
        height: 800,
        minWidth: 1281,
        minHeight: 800,
        backgroundColor: '#312450',
        show: false,
        icon: path.join(__dirname, 'assets/icons/png/64x64.png'),
        /* Specifies a script that will be loaded before other scripts run in 
        the page. This script will always have access to node APIs no matter 
        whether node integration is turned on or off. */
        webPreferences: {
            preload: path.join(__dirname, 'sentry.js')
        }
    })

    secondWindow = new BrowserWindow({
    	frame: false,
        titleBarStyle: 'hidden',
    	width: 800,
    	height: 660,
    	minWidth: 800,
    	minHeight: 660,
    	backgroundColor: '#312450',
    	show: false,
    	icon: path.join(__dirname, 'assets/icons/png/64x64.png'),
    	parent: mainWindow,
        /* Specifies a script that will be loaded before other scripvarts run in 
        the page. This script will always have access to node APIs no matter 
        whether node integration is turned on or off. */
        webPreferences: {
            preload: path.join(__dirname, 'sentry.js')
        }
    })

    // and load the index.html of the app.
    mainWindow.loadURL(`file://${__dirname}/index.html`)

    secondWindow.loadURL(`file://${__dirname}/windows/ipcwindow.html`)

    // Emitted when the window is closed.
    mainWindow.on('closed', function() {
        // Dereference the window object, usually you would store windows
        // in an array if your app supports multi windows, this is the time
        // when you should delete the corresponding element.
        mainWindow = null
    })

    require('./menu/mainmenu')

    mainWindow.once('ready-to-show', () => {
        mainWindow.show()
    })

    /* Simulate an exception for testing with Sentry */
    /*const Sentry = require('@sentry/electron');
    try {
        myEvilOperation();
    } catch (event) {
        Sentry.captureMessage("stop it now")
        Sentry.captureException(event);
    }*/
}

// Listen to open second window event from renderer process
ipcMain.on('window.open', (event, arg)=> {
	secondWindow.show()
})

// Listen to close second window event from renderer process
ipcMain.on('window.close', (event, arg)=> {
	secondWindow.hide()
})

// Crash from button in second window! Takes IPC Renderer signal from ipcwindowcrash.js
ipcMain.on('window.error', (event, arg) => {
    throw new Error(`Error triggered by wrong button click. Another test error.`)
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function() {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', function() {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (mainWindow === null) {
        createWindow()
    }
})
