const path = require('path');
const {app, BrowserWindow} = require('electron');

const isDev = app.isPackaged ? false : require('electron-is-dev');

/**
 * Creates the main window.
 *
 * @param {object} windowOptions The options for the window
 * @return {BrowserWindow} The newly created window
 */
function createWindow(windowOptions = {}) {
  newWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 600,
    minHeight: 500,
    title: 'QData',
    icon: path.join(app.getAppPath(), './public/favicon.ico'),
    autoHideMenuBar: true,
    frame: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, '../preload.js'),
    },
    ...windowOptions,
  });

  newWindow.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../../build/index.html')}`);

  if (isDev) {
    const {default: installExtension, REACT_DEVELOPER_TOOLS, REDUX_DEVTOOLS} = require('electron-devtools-installer');

    installExtension(REACT_DEVELOPER_TOOLS)
      .then((name) => console.log(`Added Extension:  ${name}`))
      .catch((err) => console.error('An error occurred: ', err));

    installExtension(REDUX_DEVTOOLS)
      .then((name) => console.log(`Added Extension:  ${name}`))
      .catch((err) => console.error('An error occurred: ', err));

    newWindow.webContents.on('did-frame-finish-load', () => {
      newWindow.webContents.openDevTools({mode: 'detach'});
    });
  }

  return newWindow;
}

module.exports = {createWindow};
