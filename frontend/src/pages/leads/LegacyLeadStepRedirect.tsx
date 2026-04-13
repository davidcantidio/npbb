import { Navigate, useSearchParams } from "react-router-dom";

type LegacyLeadStepRedirectProps = {
  step: "mapping" | "pipeline";
};

export default function LegacyLeadStepRedirect({ step }: LegacyLeadStepRedirectProps) {
  const [searchParams] = useSearchParams();
  const batchId = searchParams.get("batch_id");

  const nextParams = new URLSearchParams();
  nextParams.set("step", step);
  if (batchId) {
    nextParams.set("batch_id", batchId);
  }

  return <Navigate to={`/leads/importar?${nextParams.toString()}`} replace />;
}
