const {app, BrowserWindow, ipcMain} = require('electron');
const {createWindow} = require('./lib/window');
const {WorkerHost} = require('./lib/worker');

WorkerHost.getInstance('HOST').start();

require('./handlers/window');
require('./handlers/about');
require('./handlers/edit');
require('./handlers/file');

app.whenReady().then(() => {
  createWindow();
  ipcMain.on('app:exit', () => app.quit());
});

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
