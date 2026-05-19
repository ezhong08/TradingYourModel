import { useState, useCallback } from "react";
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ListItemText,
  Checkbox,
  OutlinedInput,
  SelectChangeEvent,
} from "@mui/material";
import { INDICATORS, Indicator } from "../types";

interface LeftPanelProps {
  symbol: string;
  onDataLoaded: (
    title: string,
    output: string,
    bullOutput?: string,
    bearOutput?: string,
  ) => void;
  onLoading: () => void;
}

type TabValue = "fundamental" | "indicator" | "model";

export default function LeftPanel({
  symbol,
  onDataLoaded,
  onLoading,
}: LeftPanelProps) {
  const [currentTab, setCurrentTab] = useState<TabValue>("fundamental");
  const [selectedIndicator, setSelectedIndicator] = useState<string>("rsi");
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([
    "rsi",
  ]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: TabValue) => {
    setCurrentTab(newValue);
  };

  const handleLoadFundamental = useCallback(async () => {
    if (!symbol) {
      alert("Please enter a stock symbol");
      return;
    }
    onLoading();
    try {
      const result = await window.api.getFundamentals(symbol);
      if (result.success) {
        onDataLoaded("Fundamentals", result.data ?? "");
      } else {
        onDataLoaded("Fundamentals", `Error: ${result.error}`);
      }
    } catch (e) {
      onDataLoaded("Fundamentals", `Error: ${(e as Error).message}`);
    }
  }, [symbol, onDataLoaded, onLoading]);

  const handleLoadIndicator = useCallback(async () => {
    if (!symbol) {
      alert("Please enter a stock symbol");
      return;
    }
    onLoading();
    try {
      const result = await window.api.getStockStatsIndicator(
        symbol,
        selectedIndicator,
      );
      if (result.success) {
        onDataLoaded("Indicator", result.data ?? "");
      } else {
        onDataLoaded("Indicator", `Error: ${result.error}`);
      }
    } catch (e) {
      onDataLoaded("Indicator", `Error: ${(e as Error).message}`);
    }
  }, [symbol, selectedIndicator, onDataLoaded, onLoading]);

  const handleAskLLM = useCallback(async () => {
    if (selectedIndicators.length === 0) {
      alert("Select at least one indicator");
      return;
    }
    if (!symbol) {
      alert("Please enter a stock symbol");
      return;
    }
    onLoading();
    try {
      const [bullResult, bearResult] = await Promise.all([
        window.api.modelBull(symbol, selectedIndicators),
        window.api.modelBear(symbol, selectedIndicators),
      ]);
      onDataLoaded(
        "Model",
        "",
        bullResult.success
          ? (bullResult.data ?? "No data")
          : `Error: ${bullResult.error}`,
        bearResult.success
          ? (bearResult.data ?? "No data")
          : `Error: ${bearResult.error}`,
      );
    } catch (e) {
      onDataLoaded(
        "Model",
        "",
        `Error: ${(e as Error).message}`,
        `Error: ${(e as Error).message}`,
      );
    }
  }, [symbol, selectedIndicators, onDataLoaded, onLoading]);

  return (
    <Box
      sx={{
        width: "40%",
        display: "flex",
        flexDirection: "column",
        borderRight: 1,
        borderColor: "secondary.main",
      }}
    >
      <Tabs
        value={currentTab}
        onChange={handleTabChange}
        sx={{
          bgcolor: "background.paper",
          borderBottom: 1,
          borderColor: "secondary.main",
          "& .MuiTabs-indicator": {
            backgroundColor: "primary.main",
          },
        }}
      >
        <Tab label="Fundamental" value="fundamental" />
        <Tab label="Indicator" value="indicator" />
        <Tab label="Model" value="model" />
      </Tabs>

      <Box sx={{ flex: 1, p: 2, overflowY: "auto" }}>
        {currentTab === "fundamental" && (
          <>
            <Typography
              variant="subtitle2"
              sx={{ color: "primary.main", mb: 2 }}
            >
              Company Fundamentals
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary", mb: 2 }}>
              View fundamental data including market cap, PE ratio, dividends,
              and more.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleLoadFundamental}
            >
              Load Fundamentals
            </Button>
          </>
        )}

        {currentTab === "indicator" && (
          <>
            <Typography
              variant="subtitle2"
              sx={{ color: "primary.main", mb: 2 }}
            >
              Technical Indicators
            </Typography>
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Select Indicator</InputLabel>
              <Select
                value={selectedIndicator}
                label="Select Indicator"
                onChange={(e) => setSelectedIndicator(e.target.value)}
              >
                {INDICATORS.map((ind: Indicator) => (
                  <MenuItem key={ind.value} value={ind.value}>
                    {ind.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button
              variant="contained"
              color="primary"
              onClick={handleLoadIndicator}
            >
              Load Indicator
            </Button>
          </>
        )}

        {currentTab === "model" && (
          <>
            <Typography
              variant="subtitle2"
              sx={{ color: "primary.main", mb: 2 }}
            >
              Model
            </Typography>
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Select Indicators</InputLabel>
              <Select
                multiple
                value={selectedIndicators}
                onChange={(e: SelectChangeEvent<string[]>) =>
                  setSelectedIndicators(e.target.value as string[])
                }
                input={<OutlinedInput label="Select Indicators" />}
                renderValue={(selected) =>
                  (selected as string[])
                    .map(
                      (v) => INDICATORS.find((i) => i.value === v)?.label ?? v,
                    )
                    .join(", ")
                }
                sx={{ maxHeight: 200 }}
              >
                {INDICATORS.map((ind: Indicator) => (
                  <MenuItem key={ind.value} value={ind.value}>
                    <Checkbox
                      checked={selectedIndicators.indexOf(ind.value) > -1}
                    />
                    <ListItemText primary={ind.label} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" color="primary" onClick={handleAskLLM}>
              Ask LLM
            </Button>
          </>
        )}
      </Box>
    </Box>
  );
}
