const path = require('path');
const {app, BrowserWindow, ipcMain, dialog} = require('electron');

app.whenReady().then(() => {
  ipcMain.handle('openFile', async (event) => {
    const currentWindow = BrowserWindow.fromId(event.frameId);

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

    // TODO Replace timeout with actual file reading logic
    await new Promise((resolve) => setTimeout(resolve, 2000));

    currentWindow.webContents.send('openedFile', {path: filePath, name: path.basename(filePath)});

    return filePath;
  });

  ipcMain.on('closeFile', (event) => {
    const currentWindow = BrowserWindow.fromId(event.frameId);
    currentWindow.webContents.send('closedFile');
  });
});
