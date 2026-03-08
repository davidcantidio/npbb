import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
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
          p: 0.25,
          color: "text.secondary",
        }}
      >
        <InfoOutlinedIcon sx={{ fontSize: 14 }} />
      </IconButton>
    </Tooltip>
  );
}

export type { InfoTooltipProps };
