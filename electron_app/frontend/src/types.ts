export interface ApiResult {
  success: boolean;
  data?: string;
  error?: string;
}

export interface Indicator {
  value: string;
  label: string;
}

export const INDICATORS: Indicator[] = [
  { value: "rsi", label: "RSI" },
  { value: "macd", label: "MACD" },
  { value: "macds", label: "MACD Signal" },
  { value: "macdh", label: "MACD Histogram" },
  { value: "close_50_sma", label: "50 SMA" },
  { value: "close_200_sma", label: "200 SMA" },
  { value: "close_10_ema", label: "10 EMA" },
  { value: "boll", label: "Bollinger Middle" },
  { value: "boll_ub", label: "Bollinger Upper" },
  { value: "boll_lb", label: "Bollinger Lower" },
  { value: "atr", label: "ATR" },
  { value: "vwma", label: "VWMA" },
  { value: "mfi", label: "MFI" },
];

export interface ElectronAPI {
  getFundamentals: (symbol: string) => Promise<ApiResult>;
  getStockStatsIndicator: (
    symbol: string,
    indicator: string,
    currDate?: string,
    lookBackDays?: number,
  ) => Promise<ApiResult>;
  modelBull: (
    symbol: string,
    indicators: string[],
    includeFundamental?: boolean,
  ) => Promise<ApiResult>;
  modelBear: (
    symbol: string,
    indicators: string[],
    includeFundamental?: boolean,
  ) => Promise<ApiResult>;
}

declare global {
  interface Window {
    api: ElectronAPI;
  }
}
