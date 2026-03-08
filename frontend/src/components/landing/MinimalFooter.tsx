import { Link, Stack, Typography } from "@mui/material";

type MinimalFooterProps = {
  tagline: string;
  textColor: string;
  privacyPolicyUrl: string;
};

export default function MinimalFooter({
  tagline,
  textColor,
  privacyPolicyUrl,
}: MinimalFooterProps) {
  return (
    <Stack
      component="footer"
      data-testid="minimal-footer"
      direction={{ xs: "column", md: "row" }}
      spacing={2}
      justifyContent="space-between"
      alignItems={{ xs: "flex-start", md: "center" }}
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
