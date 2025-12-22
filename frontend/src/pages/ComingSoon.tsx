import { Box, Paper, Typography } from "@mui/material";

type Props = {
  title: string;
};

export default function ComingSoon({ title }: Props) {
  return (
    <Box sx={{ width: "100%" }}>
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={900} gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Em breve.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}
