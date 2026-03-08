import { Box, Card, CardContent, Skeleton, Stack } from "@mui/material";

export function KpiCardSkeleton() {
  return (
    <Card data-testid="kpi-card-skeleton" variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
            <Box sx={{ width: "100%" }}>
              <Skeleton variant="text" width="42%" height={16} />
              <Skeleton variant="text" width="60%" height={38} />
            </Box>
            <Skeleton variant="rounded" width={44} height={44} />
          </Box>

          <Skeleton variant="text" width="90%" height={18} />

          <Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", gap: 1, mb: 0.75 }}>
              <Skeleton variant="text" width="28%" height={14} />
              <Skeleton variant="text" width="18%" height={14} />
            </Box>
            <Skeleton variant="rounded" height={8} />
          </Box>

          <Skeleton variant="text" width="80%" height={14} />
        </Stack>
      </CardContent>
    </Card>
  );
}
