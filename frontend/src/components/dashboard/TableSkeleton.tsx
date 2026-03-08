import { Card, CardContent, Skeleton, Stack } from "@mui/material";

export function TableSkeleton() {
  return (
    <Card data-testid="table-skeleton" variant="outlined">
      <CardContent>
        <Stack spacing={1.5}>
          <Skeleton variant="text" width={180} height={28} />
          <Skeleton variant="rounded" height={34} />
          <Skeleton variant="rounded" height={34} />
          <Skeleton variant="rounded" height={34} />
          <Skeleton variant="rounded" height={34} />
          <Skeleton variant="rounded" height={34} />
        </Stack>
      </CardContent>
    </Card>
  );
}
