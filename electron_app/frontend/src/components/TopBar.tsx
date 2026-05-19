import { Box, TextField, Typography } from "@mui/material";

interface TopBarProps {
  symbol: string;
  onSymbolChange: (symbol: string) => void;
}

export default function TopBar({ symbol, onSymbolChange }: TopBarProps) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        p: 2,
        bgcolor: "background.paper",
        borderBottom: 1,
        borderColor: "secondary.main",
      }}
    >
      <Typography
        variant="h6"
        sx={{ color: "primary.main", fontWeight: "bold", mr: 1 }}
      >
        TradingYourModel
      </Typography>
      <TextField
        label="Stock Symbol"
        value={symbol}
        onChange={(e) => onSymbolChange(e.target.value.toUpperCase())}
        size="small"
        sx={{ width: 150 }}
        inputProps={{ style: { fontSize: "1rem" } }}
      />
    </Box>
  );
}
