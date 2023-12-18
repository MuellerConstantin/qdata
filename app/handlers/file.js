const path = require('path');
const {app, BrowserWindow, ipcMain, dialog} = require('electron');

app.whenReady().then(() => {
  ipcMain.handle('openFile', () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];

    return dialog
      .showOpenDialog({
        properties: ['openFile'],
        title: 'Open File',
        filters: [{name: 'QVD', extensions: ['qvd']}],
      })
      .then(({canceled, filePaths}) => {
        if (canceled) {
          return null;
        }

        const filePath = filePaths[0];

        mainWindow.webContents.send('openingFile', {path: filePath, name: path.basename(filePath)});

        return filePath;
      })
      .then((filePath) => {
        // TODO Replace timeout with actual file reading logic
        return new Promise((resolve) => setTimeout(resolve, 2000)).then(() => filePath);
      })
      .then((filePath) => {
        mainWindow.webContents.send('openedFile', {path: filePath, name: path.basename(filePath)});

        return filePath;
      });
  });

  ipcMain.on('closeFile', () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    mainWindow.webContents.send('closedFile');
  });
});
