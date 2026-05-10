require('dotenv').config();
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;

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

// Helper function to call Python bridge
function callPythonBridge(args) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, 'python_bridge.py');
    const python = spawn('python', [pythonScript, ...args], {
      cwd: path.join(__dirname, '..'),
      stdio: 'pipe'
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`Python stderr: ${data}`);
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Python process exited with code ${code}`));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse Python output: ${stdout}`));
      }
    });

    python.on('error', (err) => {
      reject(err);
    });
  });
}

// IPC Handlers
ipcMain.handle('get_fundamentals', async (event, symbol) => {
  try {
    const result = await callPythonBridge(['get_fundamentals', symbol]);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get_stock_stats_indicators_window', async (event, symbol, indicator, currDate, lookBackDays) => {
  try {
    const args = ['get_indicator', symbol, indicator];
    if (currDate) args.push(currDate);
    if (lookBackDays) args.push(lookBackDays.toString());
    const result = await callPythonBridge(args);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('model_bull', async (event, symbol, indicators) => {
  try {
    const result = await callPythonBridge(['model_bull', symbol, JSON.stringify(indicators)]);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('model_bear', async (event, symbol, indicators) => {
  try {
    const result = await callPythonBridge(['model_bear', symbol, JSON.stringify(indicators)]);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

app.whenReady().then(() => {
  createWindow();
});

app.on('window-all-closed', () => {
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});