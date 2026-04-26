const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getFundamentals: (symbol) => ipcRenderer.invoke('get_fundamentals', symbol),
  getStockStatsIndicator: (symbol, indicator, currDate, lookBackDays) =>
    ipcRenderer.invoke('get_stock_stats_indicators_window', symbol, indicator, currDate, lookBackDays)
});
