import { IconButton, Tooltip, type TooltipProps } from "@mui/material";

type InfoTooltipProps = {
  label: string;
  description: string;
  placement?: TooltipProps["placement"];
};

export function InfoTooltip({ label, description, placement = "top" }: InfoTooltipProps) {
  return (
    <Tooltip title={description} placement={placement} describeChild>
      <IconButton
        size="small"
        aria-label={`Saiba mais sobre ${label}`}
        sx={{
          p: 0,
          width: 18,
          height: 18,
          borderRadius: 999,
          color: "text.secondary",
          fontSize: 13,
          lineHeight: 1,
        }}
      >
        ℹ️
      </IconButton>
    </Tooltip>
  );
}

export type { InfoTooltipProps };
