const path = require('path');
const {app, BrowserWindow, ipcMain, dialog} = require('electron');
const {createWindow} = require('../lib/window');
const {QvdFile} = require('../lib/qvd');

let currentFile = null;

app.whenReady().then(() => {
  ipcMain.on('newWindow', async (event) => {
    createWindow();
  });

  ipcMain.handle('openFile', async (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);

    const {canceled, filePaths} = await dialog.showOpenDialog({
      properties: ['openFile'],
      title: 'Open File',
      filters: [{name: 'QVD', extensions: ['qvd']}],
    });

    if (canceled) {
      return null;
    }

    const filePath = filePaths[0];

    currentWindow.webContents.send('openingFile', {path: filePath, name: path.basename(filePath)});

    try {
      currentFile = new QvdFile(filePath);
      await currentFile.load();

      currentWindow.webContents.send('openedFile', {
        path: filePath,
        name: path.basename(filePath),
        table: currentFile.getTable(),
      });

      return filePath;
    } catch (err) {
      console.error(err);

      currentWindow.webContents.send('openingFileFailed', {
        path: filePath,
        name: path.basename(filePath),
        error: err,
      });

      return null;
    }
  });

  ipcMain.on('closeFile', (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);

    currentFile = null;

    currentWindow.webContents.send('closedFile');
  });
});
