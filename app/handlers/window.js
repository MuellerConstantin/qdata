const {app, BrowserWindow, ipcMain} = require('electron');
const {createWindow} = require('../lib/window');

/**
 * Creates a new window.
 */
function createNewWindow() {
  createWindow();
}

/**
 * Quits the app immediately.
 */
function exitApp() {
  app.quit();
}

/**
 * Closes the given window.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to close.
 */
function closeWindow(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);
  currentWindow.close();
}

/**
 * Minimizes the given window.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to minimize.
 */
function minimizeWindow(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);
  currentWindow.minimize();
}

/**
 * Maximizes the given window.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to maximize.
 */
function maximizeWindow(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);

  if (currentWindow.isMaximized()) {
    currentWindow.unmaximize();
  } else {
    currentWindow.maximize();
  }
}

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
  ipcMain.on('newWindow', () => createNewWindow());
  ipcMain.on('exitApp', () => exitApp());
  ipcMain.on('closeWindow', (event) => closeWindow(event.sender));
  ipcMain.on('minimizeWindow', (event) => minimizeWindow(event.sender));
  ipcMain.on('maximizeWindow', (event) => maximizeWindow(event.sender));
  ipcMain.on('triggerCopyToClipboard', (event) => triggerCopyToClipboard(event.sender));
});
