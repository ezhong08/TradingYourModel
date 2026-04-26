const { app, BrowserWindow, ipcMain } = require('electron');

let mainWindow;
let apiServer = null;

async function startApiServer() {
  const { spawn } = require('child_process');
  apiServer = spawn('python', ['server.py'], {
    cwd: __dirname,
    stdio: 'pipe'
  });
  apiServer.stdout.on('data', (data) => console.log(`Server: ${data}`));
  apiServer.stderr.on('data', (data) => console.error(`Server error: ${data}`));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');

  if (process.argv.includes('--enable-logging')) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  startApiServer().then(createWindow);
});

app.on('window-all-closed', () => {
  if (apiServer) apiServer.kill();
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

const path = require('path');
