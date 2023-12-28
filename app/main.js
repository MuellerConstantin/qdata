const {app, BrowserWindow} = require('electron');
const {createWindow} = require('./lib/window');

require('./handlers/window');
require('./handlers/about');
require('./handlers/file');

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
