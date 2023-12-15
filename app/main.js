const path = require('path');
const os = require('os');
const {app, BrowserWindow, ipcMain} = require('electron');

const isDev = app.isPackaged ? false : require('electron-is-dev');

let mainWindow;

/**
 * Creates the main window.
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 600,
    minHeight: 400,
    title: 'QData',
    icon: path.join(app.getAppPath(), './public/favicon.ico'),
    autoHideMenuBar: true,
    frame: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../build/index.html')}`);

  if (isDev) {
    mainWindow.webContents.on('did-frame-finish-load', () => {
      mainWindow.webContents.openDevTools({mode: 'detach'});
    });
  }
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.on('closeWindow', () => {
    mainWindow?.close();
  });

  ipcMain.on('minimizeWindow', () => {
    mainWindow?.minimize();
  });

  ipcMain.on('maximizeWindow', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow?.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });

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
