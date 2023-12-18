const os = require('os');
const {app, ipcMain} = require('electron');

app.whenReady().then(() => {
  ipcMain.handle('getArchInfo', () => {
    return process.arch;
  });

  ipcMain.handle('getAppVersion', () => {
    return app.getVersion();
  });

  ipcMain.handle('getElectronVersion', () => {
    return process.versions.electron;
  });

  ipcMain.handle('getNodeVersion', () => {
    return process.versions.node;
  });

  ipcMain.handle('getV8Version', () => {
    return process.versions.v8;
  });

  ipcMain.handle('getOsInfo', () => {
    return `${os.type()} ${os.arch()} ${os.release()}`;
  });
});
