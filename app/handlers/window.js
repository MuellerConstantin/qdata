const {app, BrowserWindow, ipcMain} = require('electron');

app.whenReady().then(() => {
  ipcMain.on('closeWindow', () => {
    const currentWindow = BrowserWindow.getAllWindows()[0];
    currentWindow.close();
  });

  ipcMain.on('minimizeWindow', () => {
    const currentWindow = BrowserWindow.getAllWindows()[0];
    currentWindow.minimize();
  });

  ipcMain.on('maximizeWindow', () => {
    const currentWindow = BrowserWindow.getAllWindows()[0];

    if (currentWindow.isMaximized()) {
      currentWindow.unmaximize();
    } else {
      currentWindow.maximize();
    }
  });

  ipcMain.on('triggerCopyToClipboard', () => {
    const currentWindow = BrowserWindow.getAllWindows()[0];

    currentWindow.webContents.sendInputEvent({type: 'keyDown', keyCode: 'c', modifiers: ['control']});
  });
});
