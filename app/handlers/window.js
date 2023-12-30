const {app, BrowserWindow, ipcMain} = require('electron');
const {createWindow} = require('../lib/window');

/**
 * Creates a new window.
 */
function createNewWindow() {
  createWindow();
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

app.whenReady().then(() => {
  ipcMain.on('window:new', () => createNewWindow());
  ipcMain.on('window:close', (event) => closeWindow(event.sender));
  ipcMain.on('window:minimize', (event) => minimizeWindow(event.sender));
  ipcMain.on('window:maximize', (event) => maximizeWindow(event.sender));
});
