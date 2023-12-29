const path = require('path');
const fs = require('fs');
const {app, BrowserWindow, ipcMain, dialog} = require('electron');
const {QvdFile} = require('../lib/qvd');

let currentFile = null;

/**
 * Opens a file.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to open the file in.
 * @return {string} The path of the opened file.
 */
async function openFile(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);

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

    await addRecentFile(filePath);

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
}

/**
 * Closes the current file in the given window.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to close the file in.
 */
function closeFile(webContents) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);

  currentFile = null;

  currentWindow.webContents.send('closedFile');
}

/**
 * Adds a file to the list of recent files.
 *
 * @param {string} filePath The path of the file to add.
 */
async function addRecentFile(filePath) {
  const recentFilesPath = path.join(app.getPath('userData'), 'recentFiles.json');

  let recentFiles = null;

  if (fs.existsSync(recentFilesPath)) {
    const recentFilesData = await fs.promises.readFile(recentFilesPath);
    recentFiles = new Set(JSON.parse(recentFilesData));
  } else {
    recentFiles = new Set();
  }

  recentFiles.add(filePath);

  const recentFilesData = JSON.stringify([...recentFiles]);
  await fs.promises.writeFile(recentFilesPath, recentFilesData);

  BrowserWindow.getAllWindows().forEach((window) => window.webContents.send('recentFilesChanged', [...recentFiles]));
}

/**
 * Clears the list of recent files.
 */
async function clearRecentFiles() {
  const recentFilesPath = path.join(app.getPath('userData'), 'recentFiles.json');

  await fs.promises.writeFile(recentFilesPath, JSON.stringify([]));

  BrowserWindow.getAllWindows().forEach((window) => window.webContents.send('recentFilesChanged', []));
}

/**
 * Returns the list of recent files.
 *
 * @return {Array<string>} The list of recent files.
 */
async function getRecentFiles() {
  const recentFilesPath = path.join(app.getPath('userData'), 'recentFiles.json');

  if (!fs.existsSync(recentFilesPath)) {
    return [];
  }

  const recentFilesData = await fs.promises.readFile(recentFilesPath);
  const recentFiles = new Set(JSON.parse(recentFilesData));

  return [...recentFiles];
}

/**
 * Opens a recently opened file directly by using the specified path.
 *
 * @param {Electron.WebContents} webContents The web contents of the window to open the file in.
 * @param {string} filePath The path of the file to open.
 * @return {string} The path of the opened file.
 */
async function openRecentFile(webContents, filePath) {
  const currentWindow = BrowserWindow.fromWebContents(webContents);

  currentWindow.webContents.send('openingFile', {path: filePath, name: path.basename(filePath)});

  try {
    currentFile = new QvdFile(filePath);
    await currentFile.load();

    currentWindow.webContents.send('openedFile', {
      path: filePath,
      name: path.basename(filePath),
      table: currentFile.getTable(),
    });

    await addRecentFile(filePath);

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
}

app.whenReady().then(() => {
  ipcMain.handle('openFile', (event) => openFile(event.sender));
  ipcMain.on('closeFile', (event) => closeFile(event.sender));
  ipcMain.on('addRecentFile', (event, path) => addRecentFile(path));
  ipcMain.on('clearRecentFiles', () => clearRecentFiles());
  ipcMain.handle('getRecentFiles', () => getRecentFiles());
  ipcMain.handle('openRecentFile', (event, filePath) => openRecentFile(event.sender, filePath));
});
