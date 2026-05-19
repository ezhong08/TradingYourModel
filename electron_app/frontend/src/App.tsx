import { useState } from "react";
import { Box, CssBaseline, ThemeProvider } from "@mui/material";
import theme from "./theme";
import TopBar from "./components/TopBar";
import LeftPanel from "./components/LeftPanel";
import RightPanel from "./components/RightPanel";

export default function App() {
  const [symbol, setSymbol] = useState("AAPL");
  const [rightTitle, setRightTitle] = useState("Output");
  const [output, setOutput] = useState(
    "Enter a stock symbol and click a tab to view data.",
  );
  const [isPlaceholder, setIsPlaceholder] = useState(true);
  const [bullOutput, setBullOutput] = useState<string | undefined>();
  const [bearOutput, setBearOutput] = useState<string | undefined>();

  const handleDataLoaded = (
    title: string,
    data: string,
    bull?: string,
    bear?: string,
  ) => {
    setRightTitle(title);
    setOutput(data);
    setIsPlaceholder(false);
    setBullOutput(bull);
    setBearOutput(bear);
  };

  const handleLoading = () => {
    setOutput("Loading...");
    setIsPlaceholder(false);
    setBullOutput(undefined);
    setBearOutput(undefined);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100vh",
        }}
      >
        <TopBar symbol={symbol} onSymbolChange={setSymbol} />
        <Box sx={{ flex: 1, display: "flex", overflow: "hidden" }}>
          <LeftPanel
            symbol={symbol}
            onDataLoaded={handleDataLoaded}
            onLoading={handleLoading}
          />
          <RightPanel
            title={rightTitle}
            output={output}
            isPlaceholder={isPlaceholder}
            bullOutput={bullOutput}
            bearOutput={bearOutput}
          />
        </Box>
      </Box>
    </ThemeProvider>
  );
}
