import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#e94560",
    },
    secondary: {
      main: "#0f3460",
    },
    background: {
      default: "#1a1a2e",
      paper: "#16213e",
    },
    text: {
      primary: "#eee",
      secondary: "#aaa",
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          height: "100vh",
          margin: 0,
          padding: 0,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontSize: "0.9rem",
          "&.Mui-selected": {
            color: "#e94560",
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#0f3460",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "#e94560",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "#e94560",
          },
        },
        input: {
          color: "#eee",
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: "#aaa",
          "&.Mui-focused": {
            color: "#e94560",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
  },
});

export default theme;
