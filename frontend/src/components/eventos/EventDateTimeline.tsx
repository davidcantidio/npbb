import { Box, Stack, Typography } from "@mui/material";
import { useMemo } from "react";

const MS_PER_DAY = 1000 * 60 * 60 * 24;

type TimelineStatus = "upcoming" | "ongoing" | "past";

export type EventDateTimelineProps = {
  startDate?: string | null;
  endDate?: string | null;
};

function parseISODate(value?: string | null): Date | null {
  if (!value) return null;
  const [y, m, d] = value.split("-").map((part) => Number(part));
  if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
  if (y < 1000 || m < 1 || m > 12 || d < 1 || d > 31) return null;
  const date = new Date(y, m - 1, d);
  if (Number.isNaN(date.getTime())) return null;
  if (date.getFullYear() !== y || date.getMonth() !== m - 1 || date.getDate() !== d) return null;
  return date;
}

function startOfToday(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

function formatShortDate(date: Date): string {
  const day = String(date.getDate()).padStart(2, "0");
  const rawMonth = new Intl.DateTimeFormat("pt-BR", { month: "short" })
    .format(date)
    .replace(/\./g, "");
  const month = rawMonth ? rawMonth[0].toUpperCase() + rawMonth.slice(1) : rawMonth;
  return `${day} ${month}`;
}

function buildTimelineInfo(start: Date, end: Date) {
  const today = startOfToday();
  const startTime = start.getTime();
  const endTime = end.getTime();
  const todayTime = today.getTime();

  const totalDaysInclusive = Math.max(1, Math.floor((endTime - startTime) / MS_PER_DAY) + 1);
  const isSameDay = startTime === endTime;
  const status: TimelineStatus = todayTime < startTime ? "upcoming" : todayTime > endTime ? "past" : "ongoing";
  const daysUntilStart = Math.max(0, Math.ceil((startTime - todayTime) / MS_PER_DAY));
  const daysRemaining = Math.max(0, Math.ceil((endTime - todayTime) / MS_PER_DAY));
  const daysSinceEnd = Math.max(0, Math.floor((todayTime - endTime) / MS_PER_DAY));

  const elapsedDays = Math.max(0, Math.floor((todayTime - startTime) / MS_PER_DAY) + 1);
  const filledCount =
    status === "past"
      ? totalDaysInclusive
      : status === "ongoing"
        ? Math.min(totalDaysInclusive, Math.max(1, elapsedDays))
        : 0;
  const daysCountdown = status === "upcoming" ? daysUntilStart : daysRemaining;

  return {
    filledCount,
    startLabel: formatShortDate(start),
    endLabel: formatShortDate(end),
    isSameDay,
    status,
    daysCountdown,
    daysSinceEnd,
    totalDaysInclusive,
  };
}

export function EventDateTimeline({ startDate, endDate }: EventDateTimelineProps) {
  const start = useMemo(() => parseISODate(startDate), [startDate]);
  const end = useMemo(() => parseISODate(endDate), [endDate]);

  if (!start && !end) {
    return (
      <Typography variant="body2" color="text.secondary">
        Sem data definida
      </Typography>
    );
  }

  const effectiveStart = start ?? end;
  const effectiveEnd = end ?? start;

  if (!effectiveStart || !effectiveEnd) {
    return (
      <Typography variant="body2" color="text.secondary">
        Sem data definida
      </Typography>
    );
  }

  const timeline = buildTimelineInfo(effectiveStart, effectiveEnd);
  const isSingle = timeline.isSameDay || (!start || !end);

  if (isSingle) {
    const label = formatShortDate(effectiveStart);
    const today = startOfToday().getTime();
    const dateTime = effectiveStart.getTime();
    const status: TimelineStatus = today < dateTime ? "upcoming" : today > dateTime ? "past" : "ongoing";
    const daysUntil = Math.max(0, Math.ceil((dateTime - today) / MS_PER_DAY));
    const daysSince = Math.max(0, Math.floor((today - dateTime) / MS_PER_DAY));

    return (
      <Stack spacing={0.2} alignItems="flex-start">
        <Typography
          variant="body1"
          fontWeight={700}
          sx={{ whiteSpace: "nowrap", fontSize: "1rem", lineHeight: 1.1 }}
        >
          {label}
        </Typography>
        <Box
          sx={{
            px: 0.7,
            py: 0.15,
            borderRadius: 999,
            border: "1px solid",
            borderColor: "grey.300",
            bgcolor: status === "past" ? "grey.50" : "grey.100",
            width: "fit-content",
          }}
        >
          <Typography
            variant="caption"
            fontWeight={700}
            color={status === "past" ? "text.secondary" : "text.primary"}
            sx={{ whiteSpace: "nowrap" }}
          >
            {status === "past" ? `Encerrado há ${daysSince}d` : `D-${daysUntil}`}
          </Typography>
        </Box>
      </Stack>
    );
  }

  const dotSize = 4;
  const dotGap = 2;
  const dotCount = timeline.totalDaysInclusive;
  const dotsWidth = dotCount * dotSize + (dotCount - 1) * dotGap;
  const filledColor = timeline.status === "past" ? "info.main" : "success.main";
  const baseDotColor = timeline.status === "upcoming" ? "grey.400" : "grey.300";

  return (
    <Stack spacing={0.4}>
      <Stack direction="row" spacing={1} alignItems="flex-start">
        <Stack spacing={0.15} sx={{ minWidth: 60 }} alignItems="flex-start">
          <Typography
            variant="body1"
            fontWeight={700}
            sx={{ whiteSpace: "nowrap", fontSize: "1rem", lineHeight: 1.1 }}
          >
            {timeline.startLabel}
          </Typography>
          <Box
            sx={{
              px: 0.7,
              py: 0.15,
              borderRadius: 999,
              border: "1px solid",
              borderColor: "grey.300",
              bgcolor: timeline.status === "past" ? "grey.50" : "grey.100",
              width: "fit-content",
            }}
          >
            <Typography
              variant="caption"
              fontWeight={700}
              color={timeline.status === "past" ? "text.secondary" : "text.primary"}
              sx={{ whiteSpace: "nowrap" }}
            >
              {timeline.status === "past" ? `Encerrado há ${timeline.daysSinceEnd}d` : `D-${timeline.daysCountdown}`}
            </Typography>
          </Box>
        </Stack>
        <Box
          role="progressbar"
          aria-label={`Período do evento: ${timeline.startLabel} a ${timeline.endLabel}.`}
          aria-valuenow={timeline.filledCount}
          aria-valuemin={0}
          aria-valuemax={dotCount}
          sx={{
            position: "relative",
            width: dotsWidth,
            display: "flex",
            alignItems: "center",
            gap: `${dotGap}px`,
            height: dotSize,
            flexShrink: 0,
            alignSelf: "center",
            "&:before": {
              content: '""',
              position: "absolute",
              left: 0,
              right: 0,
              top: "50%",
              borderTop: "1px dotted",
              borderColor: "grey.300",
              transform: "translateY(-50%)",
            },
          }}
        >
          {Array.from({ length: dotCount }).map((_, idx) => (
            <Box
              key={`dot-${idx}`}
              sx={{
                position: "relative",
                zIndex: 1,
                width: dotSize,
                height: dotSize,
                borderRadius: "50%",
                bgcolor:
                  timeline.status === "past"
                    ? filledColor
                    : idx < timeline.filledCount
                      ? filledColor
                      : baseDotColor,
              }}
            />
          ))}
        </Box>
        <Typography
          variant="body1"
          fontWeight={700}
          sx={{
            minWidth: 44,
            textAlign: "right",
            whiteSpace: "nowrap",
            fontSize: "1rem",
            lineHeight: 1.1,
          }}
        >
          {timeline.endLabel}
        </Typography>
      </Stack>
    </Stack>
  );
}
