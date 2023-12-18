const {app, BrowserWindow, ipcMain} = require('electron');

app.whenReady().then(() => {
  ipcMain.on('closeWindow', () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    mainWindow?.close();
  });

  ipcMain.on('minimizeWindow', () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    mainWindow?.minimize();
  });

  ipcMain.on('maximizeWindow', () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];

    if (mainWindow?.isMaximized()) {
      mainWindow?.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });
});
