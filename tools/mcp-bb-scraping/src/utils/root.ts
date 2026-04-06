import { resolve } from "node:path";

export function resolvePipelineRoot(): string {
  const env = (process.env.PIPELINE_ROOT ?? process.env.MCP_ROOT ?? "").trim();
  if (env) {
    return resolve(env);
  }
  return resolve(__dirname, "..", "..");
}
