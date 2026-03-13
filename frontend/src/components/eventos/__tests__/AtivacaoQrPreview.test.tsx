import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import AtivacaoQrPreview, {
  QR_DOWNLOAD_ERROR_MESSAGE,
  QR_PLACEHOLDER_MESSAGE,
  buildQrDownloadFilename,
  inferQrFileExtension,
} from "../AtivacaoQrPreview";

const originalCreateObjectURL = URL.createObjectURL;
const originalRevokeObjectURL = URL.revokeObjectURL;

function mockBrowserDownloadApis() {
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    writable: true,
    value: vi.fn(() => "blob:qr-download"),
  });
  Object.defineProperty(URL, "revokeObjectURL", {
    configurable: true,
    writable: true,
    value: vi.fn(),
  });
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();

  if (originalCreateObjectURL) {
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      writable: true,
      value: originalCreateObjectURL,
    });
  } else {
    delete (URL as { createObjectURL?: typeof URL.createObjectURL }).createObjectURL;
  }

  if (originalRevokeObjectURL) {
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      writable: true,
      value: originalRevokeObjectURL,
    });
  } else {
    delete (URL as { revokeObjectURL?: typeof URL.revokeObjectURL }).revokeObjectURL;
  }
});

describe("AtivacaoQrPreview", () => {
  it("infers svg and png extensions consistently", () => {
    expect(inferQrFileExtension("image/svg+xml", "https://cdn.example/qr")).toBe("svg");
    expect(inferQrFileExtension("", "data:image/svg+xml;base64,AAA")).toBe("svg");
    expect(inferQrFileExtension("image/png", "https://cdn.example/qr.png")).toBe("png");
    expect(buildQrDownloadFilename(7, "svg")).toBe("ativacao-7-qr.svg");
  });

  it("renders a placeholder and keeps download disabled when qr is missing", () => {
    render(<AtivacaoQrPreview ativacaoId={9} nome="Ativacao sem QR" qrCodeUrl={null} />);

    expect(screen.getByTestId("ativacao-qr-placeholder")).toHaveTextContent(QR_PLACEHOLDER_MESSAGE);
    expect(screen.getByRole("button", { name: /baixar qr/i })).toBeDisabled();
  });

  it("downloads the qr preserving the svg extension", async () => {
    mockBrowserDownloadApis();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      blob: vi.fn().mockResolvedValue(new Blob(["<svg/>"], { type: "image/svg+xml" })),
    } as unknown as Response);
    vi.stubGlobal("fetch", fetchMock);

    const clickSpy = vi.fn();
    let createdAnchor: unknown = null;
    const realCreateElement = document.createElement.bind(document);
    const removeChildSpy = vi.spyOn(document.body, "removeChild");
    vi.spyOn(document, "createElement").mockImplementation((tagName: string) => {
      const element = realCreateElement(tagName);
      if (tagName.toLowerCase() === "a") {
        createdAnchor = element;
        Object.defineProperty(element, "click", {
          configurable: true,
          value: clickSpy,
        });
      }
      return element;
    });

    render(<AtivacaoQrPreview ativacaoId={7} nome="Stand Principal" qrCodeUrl="https://cdn.example/qr-7.svg" />);

    await userEvent.click(screen.getByRole("button", { name: /baixar qr/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("https://cdn.example/qr-7.svg"));
    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));

    expect(createdAnchor).not.toBeNull();
    if (!createdAnchor) {
      throw new Error("Anchor de download nao foi criado.");
    }
    const anchor = createdAnchor as HTMLAnchorElement;
    expect(anchor.download).toBe("ativacao-7-qr.svg");
    expect(anchor.href).toBe("blob:qr-download");
    expect(removeChildSpy).toHaveBeenCalledWith(anchor);
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:qr-download");
  });

  it("surfaces an explicit error when qr download fails", async () => {
    mockBrowserDownloadApis();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network_error")));

    render(<AtivacaoQrPreview ativacaoId={5} nome="Stand Secundario" qrCodeUrl="https://cdn.example/qr-5.png" />);

    await userEvent.click(screen.getByRole("button", { name: /baixar qr/i }));

    expect(await screen.findByText(QR_DOWNLOAD_ERROR_MESSAGE)).toBeInTheDocument();
  });
});
