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
    <Box display="flex" justifyContent="space-between" gap={2} pt={1}>
      <Box>{leftActions}</Box>
      <Stack direction="row" spacing={2}>
        {rightActions}
      </Stack>
    </Box>
  );
}
