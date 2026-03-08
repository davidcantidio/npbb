import { Card, CardContent, Skeleton, Stack } from "@mui/material";

export function ChartSkeleton() {
  return (
    <Card data-testid="chart-skeleton" variant="outlined">
      <CardContent>
        <Stack spacing={1.5}>
          <Skeleton variant="text" width={260} height={28} />
          <Skeleton variant="text" width="58%" height={18} />
          <Skeleton variant="rounded" height={340} />
        </Stack>
      </CardContent>
    </Card>
  );
}
