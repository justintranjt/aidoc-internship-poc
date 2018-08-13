const { ipcRenderer } = require('electron')

window.openWindow = () => {
    ipcRenderer.send('window.open')
}

window.closeWindow = () => {
    ipcRenderer.send('window.close')
}

// Triggered by clicking close button on 2nd window. Send error to main process
window.crashMain = () => {
    ipcRenderer.send('window.error')
}