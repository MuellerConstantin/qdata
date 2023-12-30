const {app, BrowserWindow, ipcMain} = require('electron');

/**
 * Triggers the keyboard shortcut for copying to clipboard in the given window.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to trigger the shortcut in.
 */
function triggerCopyToClipboard(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);

  currentWindow.webContents.sendInputEvent({type: 'keyDown', keyCode: 'c', modifiers: ['control']});
}

app.whenReady().then(() => {
  ipcMain.on('edit:triggerCopyToClipboard', (event) => triggerCopyToClipboard(event.sender));
});
