import { Box, Stack } from "@mui/material";

type EventWizardActionsProps = {
  leftActions: React.ReactNode;
  rightActions: React.ReactNode;
};

/**
 * Shared action row for wizard CTA groups.
 */
export function EventWizardActions({ leftActions, rightActions }: EventWizardActionsProps) {
  return (
    <Box display="flex" justifyContent="space-between" gap={1.5} pt={1} flexWrap="wrap">
      <Box>{leftActions}</Box>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" justifyContent="flex-end">
        {rightActions}
      </Stack>
    </Box>
  );
}
