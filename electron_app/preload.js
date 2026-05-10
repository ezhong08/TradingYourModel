const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld('api', {
  getFundamentals: (symbol) => ipcRenderer.invoke('get_fundamentals', symbol),
  getStockStatsIndicator: (symbol, indicator, currDate, lookBackDays) =>
    ipcRenderer.invoke('get_stock_stats_indicators_window', symbol, indicator, currDate, lookBackDays),
  modelBull: (symbol, indicators) => ipcRenderer.invoke('model_bull', symbol, indicators),
  modelBear: (symbol, indicators) => ipcRenderer.invoke('model_bear', symbol, indicators)
});