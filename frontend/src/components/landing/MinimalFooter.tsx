import { Link, Stack, Typography } from "@mui/material";

type MinimalFooterProps = {
  tagline: string;
  textColor: string;
  privacyPolicyUrl: string;
  isPreview?: boolean;
};

export default function MinimalFooter({
  tagline,
  textColor,
  privacyPolicyUrl,
  isPreview = false,
}: MinimalFooterProps) {
  return (
    <Stack
      component="footer"
      data-testid="minimal-footer"
      direction={isPreview ? "column" : { xs: "column", md: "row" }}
      spacing={2}
      justifyContent="space-between"
      alignItems={isPreview ? "flex-start" : { xs: "flex-start", md: "center" }}
      sx={{ color: textColor }}
    >
      <Typography data-testid="minimal-footer-tagline" variant="caption" color="inherit">
        {tagline}
      </Typography>
      <Link
        data-testid="minimal-footer-link"
        href={privacyPolicyUrl}
        target="_blank"
        rel="noreferrer"
        underline="hover"
        variant="caption"
        color="inherit"
      >
        Politica de privacidade e LGPD
      </Link>
    </Stack>
  );
}
