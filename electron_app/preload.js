const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld('api', {
  getFundamentals: (symbol) => ipcRenderer.invoke('get_fundamentals', symbol),
  getStockStatsIndicator: (symbol, indicator, currDate, lookBackDays) =>
    ipcRenderer.invoke('get_stock_stats_indicators_window', symbol, indicator, currDate, lookBackDays),
  modelBull: (symbol, indicators, includeFundamental) => ipcRenderer.invoke('model_bull', symbol, indicators, includeFundamental),
  modelBear: (symbol, indicators, includeFundamental) => ipcRenderer.invoke('model_bear', symbol, indicators, includeFundamental),
  modelRecommend: (symbol, indicators, closePrice, indicatorData, fundamentalInfo, bullComment, bearComment) =>
    ipcRenderer.invoke('model_recommend', symbol, indicators, closePrice, indicatorData, fundamentalInfo, bullComment, bearComment)
});
