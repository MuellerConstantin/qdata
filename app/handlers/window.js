const {app, BrowserWindow, ipcMain} = require('electron');

app.whenReady().then(() => {
  ipcMain.on('exitApp', () => app.quit());

  ipcMain.on('closeWindow', (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);
    currentWindow.close();
  });

  ipcMain.on('minimizeWindow', (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);
    currentWindow.minimize();
  });

  ipcMain.on('maximizeWindow', (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);

    if (currentWindow.isMaximized()) {
      currentWindow.unmaximize();
    } else {
      currentWindow.maximize();
    }
  });

  ipcMain.on('triggerCopyToClipboard', (event) => {
    const currentWindow = BrowserWindow.fromWebContents(event.sender);

    currentWindow.webContents.sendInputEvent({type: 'keyDown', keyCode: 'c', modifiers: ['control']});
  });
});
