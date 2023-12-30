const os = require('os');
const {app, ipcMain} = require('electron');

app.whenReady().then(() => {
  ipcMain.handle('about:getArchInfo', () => {
    return process.arch;
  });

  ipcMain.handle('about:getAppVersion', () => {
    return app.getVersion();
  });

  ipcMain.handle('about:getElectronVersion', () => {
    return process.versions.electron;
  });

  ipcMain.handle('about:getNodeVersion', () => {
    return process.versions.node;
  });

  ipcMain.handle('about:getV8Version', () => {
    return process.versions.v8;
  });

  ipcMain.handle('about:getOsInfo', () => {
    return `${os.type()} ${os.arch()} ${os.release()}`;
  });
});
