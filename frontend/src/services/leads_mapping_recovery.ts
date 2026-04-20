import { toApiErrorCode } from "./http";
import { LeadBatch, getLeadBatch } from "./leads_import";

export const LEAD_MAPPING_RECOVERY_POLL_INTERVAL_MS = 2_500;
export const LEAD_MAPPING_RECOVERY_TIMEOUT_MS = 90_000;

export type LeadMappingRecoveryResult = {
  status: "mapped" | "pending";
  batches: LeadBatch[];
};

type LeadMappingRecoveryOptions = {
  pollIntervalMs?: number;
  timeoutMs?: number;
  getBatch?: typeof getLeadBatch;
};

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeBatchIds(batchIds: number[]) {
  const seen = new Set<number>();
  const normalized: number[] = [];
  for (const rawBatchId of batchIds) {
    const batchId = Number(rawBatchId);
    if (!Number.isFinite(batchId) || batchId <= 0 || seen.has(batchId)) {
      continue;
    }
    seen.add(batchId);
    normalized.push(batchId);
  }
  return normalized;
}

export function isLeadBatchMapped(batch: Pick<LeadBatch, "stage"> | null | undefined) {
  return batch?.stage === "silver" || batch?.stage === "gold";
}

export async function reconcileLeadMappingTimeout(
  token: string,
  batchIds: number[],
  options: LeadMappingRecoveryOptions = {},
): Promise<LeadMappingRecoveryResult> {
  const uniqueBatchIds = normalizeBatchIds(batchIds);
  if (uniqueBatchIds.length === 0) {
    return { status: "pending", batches: [] };
  }

  const pollIntervalMs = options.pollIntervalMs ?? LEAD_MAPPING_RECOVERY_POLL_INTERVAL_MS;
  const timeoutMs = options.timeoutMs ?? LEAD_MAPPING_RECOVERY_TIMEOUT_MS;
  const getBatch = options.getBatch ?? getLeadBatch;
  const deadline = Date.now() + timeoutMs;
  const lastSeenById = new Map<number, LeadBatch>();

  while (Date.now() <= deadline) {
    const results = await Promise.allSettled(uniqueBatchIds.map((batchId) => getBatch(token, batchId)));

    for (let index = 0; index < results.length; index += 1) {
      const result = results[index];
      const batchId = uniqueBatchIds[index];
      if (!batchId) {
        continue;
      }

      if (result.status === "fulfilled") {
        lastSeenById.set(batchId, result.value);
        continue;
      }

      const code = toApiErrorCode(result.reason);
      if (code === "TIMEOUT" || code === "NETWORK_ERROR") {
        continue;
      }
      throw result.reason;
    }

    if (uniqueBatchIds.every((batchId) => isLeadBatchMapped(lastSeenById.get(batchId)))) {
      return {
        status: "mapped",
        batches: uniqueBatchIds
          .map((batchId) => lastSeenById.get(batchId))
          .filter((batch): batch is LeadBatch => batch != null),
      };
    }

    if (Date.now() >= deadline) {
      break;
    }
    await wait(pollIntervalMs);
  }

  return {
    status: "pending",
    batches: uniqueBatchIds
      .map((batchId) => lastSeenById.get(batchId))
      .filter((batch): batch is LeadBatch => batch != null),
  };
}
