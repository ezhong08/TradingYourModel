import { Box, Typography, Paper } from "@mui/material";

interface RightPanelProps {
  title: string;
  output: string;
  isPlaceholder: boolean;
  bullOutput?: string;
  bearOutput?: string;
}

export default function RightPanel({
  title,
  output,
  isPlaceholder,
  bullOutput,
  bearOutput,
}: RightPanelProps) {
  return (
    <Box
      sx={{
        width: "60%",
        bgcolor: "secondary.main",
        p: 2,
        overflowY: "auto",
      }}
    >
      <Typography
        variant="subtitle1"
        sx={{ color: "primary.main", mb: 2, fontWeight: "bold" }}
      >
        {title}
      </Typography>
      <Paper
        sx={{
          bgcolor: "background.default",
          p: 2,
          minHeight: 300,
          borderRadius: 2,
        }}
      >
        {bullOutput !== undefined || bearOutput !== undefined ? (
          <>
            {bullOutput !== undefined && (
              <>
                <Typography
                  variant="subtitle2"
                  sx={{ color: "primary.main", mb: 1 }}
                >
                  Bull
                </Typography>
                <Typography
                  component="pre"
                  sx={{
                    fontFamily: "'Courier New', monospace",
                    fontSize: "0.85rem",
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    color: isPlaceholder ? "text.secondary" : "text.primary",
                    fontStyle: isPlaceholder ? "italic" : "normal",
                    mb: 2,
                  }}
                >
                  {bullOutput}
                </Typography>
              </>
            )}
            {bearOutput !== undefined && (
              <>
                <Typography
                  variant="subtitle2"
                  sx={{ color: "primary.main", mb: 1 }}
                >
                  Bear
                </Typography>
                <Typography
                  component="pre"
                  sx={{
                    fontFamily: "'Courier New', monospace",
                    fontSize: "0.85rem",
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    color: isPlaceholder ? "text.secondary" : "text.primary",
                    fontStyle: isPlaceholder ? "italic" : "normal",
                  }}
                >
                  {bearOutput}
                </Typography>
              </>
            )}
          </>
        ) : (
          <Typography
            component="pre"
            sx={{
              fontFamily: "'Courier New', monospace",
              fontSize: "0.85rem",
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              color: isPlaceholder ? "text.secondary" : "text.primary",
              fontStyle: isPlaceholder ? "italic" : "normal",
            }}
          >
            {output}
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
