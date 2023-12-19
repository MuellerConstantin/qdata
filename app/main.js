const path = require('path');
const {app, BrowserWindow} = require('electron');

require('./handlers/window');
require('./handlers/about');
require('./handlers/file');

const isDev = app.isPackaged ? false : require('electron-is-dev');

const windows = new Set();

/**
 * Creates the main window.
 */
function createWindow() {
  newWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 600,
    minHeight: 400,
    title: 'QData',
    icon: path.join(app.getAppPath(), './public/favicon.ico'),
    autoHideMenuBar: true,
    frame: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  newWindow.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../build/index.html')}`);

  if (isDev) {
    newWindow.webContents.on('did-frame-finish-load', () => {
      newWindow.webContents.openDevTools({mode: 'detach'});
    });
  }

  windows.add(newWindow);
}

app.whenReady().then(() => createWindow());

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
