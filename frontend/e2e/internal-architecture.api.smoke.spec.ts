import { expect, test } from "@playwright/test";

import {
  authHeaders,
  createApiContext,
  INVITE_TOKEN,
  loginViaApi,
  SEEDED_USER,
  uniqueNpbbEmail,
} from "./support/auth-helpers";

test("validates internal architecture endpoints and security hardening", async () => {
  const api = await createApiContext();

  try {
    const login = await loginViaApi(api);
    const headers = authHeaders(login.access_token);

    const meResponse = await api.get("/auth/me", { headers });
    expect(meResponse.status()).toBe(200);
    const meBody = (await meResponse.json()) as { email: string };
    expect(meBody.email).toBe(SEEDED_USER.email);

    const refreshResponse = await api.post("/auth/refresh", { headers });
    expect(refreshResponse.status()).toBe(200);
    const refreshBody = (await refreshResponse.json()) as {
      access_token: string;
      user: { email: string };
    };
    expect(refreshBody.access_token).toBeTruthy();
    expect(refreshBody.user.email).toBe(SEEDED_USER.email);

    const sourcesResponse = await api.get("/internal/etl/sources?limit=5", { headers });
    expect(sourcesResponse.status()).toBe(200);
    const sourcesBody = (await sourcesResponse.json()) as Array<{ source_id: string; latest_status: string | null }>;
    expect(sourcesBody.some((item) => item.source_id === "SRC_PLAYWRIGHT")).toBeTruthy();

    const ingestionsResponse = await api.get("/internal/etl/ingestions?limit=5", { headers });
    expect(ingestionsResponse.status()).toBe(200);
    const ingestionsBody = (await ingestionsResponse.json()) as Array<{ source_id: string; status: string }>;
    expect(ingestionsBody.some((item) => item.source_id === "SRC_PLAYWRIGHT" && item.status === "success")).toBeTruthy();

    const revisaoPayload = {
      workflow_id: "WF_WORKBENCH_NPBB",
      dataset_name: "dataset_npbb_test",
      actor_context: {
        actor_id: "user_npbb",
        actor_role: "npbb_reviewer",
      },
    };

    const prepareResponse = await api.post("/internal/revisao-humana/s1/prepare", {
      headers: {
        ...headers,
        "Content-Type": "application/json",
      },
      data: revisaoPayload,
    });
    expect(prepareResponse.status()).toBe(200);
    const prepareBody = (await prepareResponse.json()) as { contrato_versao: string };
    expect(prepareBody.contrato_versao).toBe("work.s1.v1");

    const executeResponse = await api.post("/internal/revisao-humana/s1/execute", {
      headers: {
        ...headers,
        "Content-Type": "application/json",
      },
      data: revisaoPayload,
    });
    expect(executeResponse.status()).toBe(200);
    const executeBody = (await executeResponse.json()) as { contrato_versao: string };
    expect(executeBody.contrato_versao).toBe("work.s1.core.v1");

    const registrationPayload = {
      email: uniqueNpbbEmail("invite-flow"),
      password: SEEDED_USER.password,
      tipo_usuario: "npbb",
    };

    const forbiddenRegistration = await api.post("/usuarios/", {
      headers: { "Content-Type": "application/json" },
      data: registrationPayload,
      failOnStatusCode: false,
    });
    expect(forbiddenRegistration.status()).toBe(403);
    expect((await forbiddenRegistration.json()).detail.code).toBe("INVITE_TOKEN_INVALID");

    const inviteRegistration = await api.post("/usuarios/", {
      headers: {
        "Content-Type": "application/json",
        "x-registration-token": INVITE_TOKEN,
      },
      data: registrationPayload,
      failOnStatusCode: false,
    });
    expect(inviteRegistration.status()).toBe(201);

    const limitedRegistration = await api.post("/usuarios/", {
      headers: {
        "Content-Type": "application/json",
        "x-registration-token": INVITE_TOKEN,
      },
      data: registrationPayload,
      failOnStatusCode: false,
    });
    expect(limitedRegistration.status()).toBe(429);
    expect((await limitedRegistration.json()).detail.code).toBe("REGISTRATION_RATE_LIMIT_EXCEEDED");

    const forgotPasswordPayload = { email: SEEDED_USER.email };

    const forgotPasswordFirst = await api.post("/usuarios/forgot-password", {
      headers: { "Content-Type": "application/json" },
      data: forgotPasswordPayload,
    });
    expect(forgotPasswordFirst.status()).toBe(200);

    const forgotPasswordSecond = await api.post("/usuarios/forgot-password", {
      headers: { "Content-Type": "application/json" },
      data: forgotPasswordPayload,
    });
    expect(forgotPasswordSecond.status()).toBe(200);

    const forgotPasswordThird = await api.post("/usuarios/forgot-password", {
      headers: { "Content-Type": "application/json" },
      data: forgotPasswordPayload,
      failOnStatusCode: false,
    });
    expect(forgotPasswordThird.status()).toBe(429);
    expect((await forgotPasswordThird.json()).detail.code).toBe("FORGOT_PASSWORD_RATE_LIMIT_EXCEEDED");
  } finally {
    await api.dispose();
  }
});
