export async function sleep(ms: number, jitterMs = 0): Promise<void> {
  const base = Math.max(0, Math.floor(ms));
  const jitter = jitterMs > 0 ? randomIntInclusive(0, Math.floor(jitterMs)) : 0;
  const duration = base + jitter;
  await new Promise<void>((resolve) => setTimeout(resolve, duration));
}

export async function sleepBetween(minMs: number, maxMs: number): Promise<void> {
  const min = Math.max(0, Math.floor(Math.min(minMs, maxMs)));
  const max = Math.max(0, Math.floor(Math.max(minMs, maxMs)));
  const duration = randomIntInclusive(min, max);
  await new Promise<void>((resolve) => setTimeout(resolve, duration));
}

function randomIntInclusive(min: number, max: number): number {
  const lo = Math.ceil(min);
  const hi = Math.floor(max);
  return Math.floor(Math.random() * (hi - lo + 1)) + lo;
}
