import { startTransition, useEffect, useRef, useState } from "react";

import { LeadImportEtlJob, getLeadImportEtlJob } from "../../../services/leads_import";
import { toApiErrorMessage } from "../../../services/http";

const POLL_INTERVAL_MS = 1200;
const ACTIVE_JOB_STATUSES = new Set(["queued", "running", "commit_queued", "committing"]);

type Params = {
  token: string | null;
};

export function useLeadImportEtlJobPolling({ token }: Params) {
  const pollTimerRef = useRef<number | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<LeadImportEtlJob | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [pollError, setPollError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (pollTimerRef.current != null) {
        window.clearTimeout(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!token || !jobId) {
      setIsPolling(false);
      return;
    }

    let cancelled = false;

    const load = async () => {
      try {
        const nextJob = await getLeadImportEtlJob(token, jobId);
        if (cancelled) return;
        startTransition(() => {
          setJob(nextJob);
          setPollError(null);
          setIsPolling(ACTIVE_JOB_STATUSES.has(nextJob.status));
        });
        if (ACTIVE_JOB_STATUSES.has(nextJob.status)) {
          pollTimerRef.current = window.setTimeout(load, POLL_INTERVAL_MS);
        } else {
          pollTimerRef.current = null;
        }
      } catch (error) {
        if (cancelled) return;
        startTransition(() => {
          setIsPolling(false);
          setPollError(toApiErrorMessage(error, "Falha ao consultar o job ETL."));
        });
        pollTimerRef.current = null;
      }
    };

    void load();

    return () => {
      cancelled = true;
      if (pollTimerRef.current != null) {
        window.clearTimeout(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [jobId, token]);

  function beginPolling(nextJobId: string) {
    if (pollTimerRef.current != null) {
      window.clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setJobId(nextJobId);
    setJob(null);
    setPollError(null);
    setIsPolling(true);
  }

  function clearJob() {
    if (pollTimerRef.current != null) {
      window.clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setJobId(null);
    setJob(null);
    setPollError(null);
    setIsPolling(false);
  }

  return {
    jobId,
    job,
    isPolling,
    pollError,
    beginPolling,
    clearJob,
  };
}
