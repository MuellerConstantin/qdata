const path = require('path');
const fs = require('fs');
const {randomUUID} = require('crypto');
const {fork} = require('child_process');
const {app, BrowserWindow, ipcMain, dialog} = require('electron');
const {WorkerHost} = require('../lib/worker');
const {QvdFileDeserializer} = require('../lib/qvd');

let currentFile = null;

/**
 * Parses a QVD file in a worker process.
 *
 * @param {string} filePath The path of the file to parse.
 * @return {Promise<any>} A promise that resolves when the file is parsed.
 */
async function parseFile(filePath) {
  const workerId = `file-${randomUUID()}`;

  /*
   * Starts a worker process that loads the file and sends it back to the main process.
   * Communication between the main process and the worker process is done via IPC. After
   * the worker process started, it connects to the worker host.
   */
  const worker = fork(path.join(__dirname, '../workers/file.js'), [workerId, filePath]);

  return new Promise((resolve, reject) => {
    WorkerHost.getInstance().on('error', (err) => reject(err), workerId);

    // Waits via IPC for the worker process to be done
    WorkerHost.getInstance()
      .join('done', workerId)
      .then(({payload}) => resolve(QvdFileDeserializer.deserialize(payload)));
  }).finally(() => worker.kill());
}

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

  currentWindow.webContents.send('file:opening', {path: filePath, name: path.basename(filePath)});

  try {
    currentFile = await parseFile(filePath);

    currentWindow.webContents.send('file:opened', {
      path: filePath,
      name: path.basename(filePath),
      table: currentFile.getTable(),
    });

    await addRecentFile(filePath);

    return filePath;
  } catch (err) {
    console.error(err);

    currentWindow.webContents.send('error:parsingFileFailed', {
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

  currentWindow.webContents.send('file:closed');
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

  BrowserWindow.getAllWindows().forEach((window) =>
    window.webContents.send('file:recentFilesChanged', [...recentFiles]),
  );
}

/**
 * Removes a file from the list of recent files.
 *
 * @param {string} filePath The path of the file to remove.
 */
async function removeRecentFile(filePath) {
  const recentFilesPath = path.join(app.getPath('userData'), 'recentFiles.json');

  let recentFiles = null;

  if (fs.existsSync(recentFilesPath)) {
    const recentFilesData = await fs.promises.readFile(recentFilesPath);
    recentFiles = new Set(JSON.parse(recentFilesData));
  } else {
    recentFiles = new Set();
  }

  recentFiles.delete(filePath);

  const recentFilesData = JSON.stringify([...recentFiles]);
  await fs.promises.writeFile(recentFilesPath, recentFilesData);

  BrowserWindow.getAllWindows().forEach((window) =>
    window.webContents.send('file:recentFilesChanged', [...recentFiles]),
  );
}

/**
 * Clears the list of recent files.
 */
async function clearRecentFiles() {
  const recentFilesPath = path.join(app.getPath('userData'), 'recentFiles.json');

  await fs.promises.writeFile(recentFilesPath, JSON.stringify([]));

  BrowserWindow.getAllWindows().forEach((window) => window.webContents.send('file:recentFilesChanged', []));
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

  currentWindow.webContents.send('file:opening', {path: filePath, name: path.basename(filePath)});

  if (!fs.existsSync(filePath)) {
    currentWindow.webContents.send('error:fileNotFound', {path: filePath, name: path.basename(filePath)});
    await removeRecentFile(filePath);
    return null;
  }

  try {
    currentFile = await parseFile(filePath);

    currentWindow.webContents.send('file:opened', {
      path: filePath,
      name: path.basename(filePath),
      table: currentFile.getTable(),
    });

    await addRecentFile(filePath);

    return filePath;
  } catch (err) {
    console.error(err);

    currentWindow.webContents.send('error:parsingFileFailed', {
      path: filePath,
      name: path.basename(filePath),
      error: err,
    });

    return null;
  }
}

app.whenReady().then(() => {
  ipcMain.handle('file:open', (event) => openFile(event.sender));
  ipcMain.on('file:close', (event) => closeFile(event.sender));
  ipcMain.on('file:addRecentFile', (event, path) => addRecentFile(path));
  ipcMain.on('file:clearRecentFiles', () => clearRecentFiles());
  ipcMain.handle('file:getRecentFiles', () => getRecentFiles());
  ipcMain.handle('file:openRecentFile', (event, filePath) => openRecentFile(event.sender, filePath));
});
