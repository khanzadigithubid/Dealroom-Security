import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import QuestionnairesPage from "./QuestionnairesPage";

function jsonResponse(status: number, body: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => body,
  } as unknown as Response;
}

const UPLOADED = {
  id: 1,
  title: "Acme Q4",
  buyer_name: "Acme",
  uploaded_at: new Date().toISOString(),
  question_count: 9,
};

describe("QuestionnairesPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("resets the form and loads the new questionnaire after upload", async () => {
    let uploaded = false;
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/questionnaires/upload") {
        uploaded = true;
        return jsonResponse(200, UPLOADED);
      }
      if (url === "/api/questionnaires") {
        return jsonResponse(200, uploaded ? [UPLOADED] : []);
      }
      throw new Error(`unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(
      <MemoryRouter>
        <QuestionnairesPage />
      </MemoryRouter>,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Title"), "Acme Q4");
    await user.upload(
      screen.getByLabelText(/Question file/),
      new File(["question\nDo you enforce MFA?"], "buyer.csv", { type: "text/csv" }),
    );

    // jsdom does not validate file inputs, so submit the form directly
    // (real browsers enforce the `required` attribute on the file input).
    const form = container.querySelector("form");
    expect(form).not.toBeNull();
    fireEvent.submit(form!);

    await waitFor(() => expect(screen.getByText("Acme Q4")).toBeInTheDocument());
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/questionnaires/upload",
      expect.objectContaining({ method: "POST" }),
    );
    expect(container.querySelector(".alert-error")).toBeNull();
    expect(screen.queryByText(/Cannot read properties of null/)).toBeNull();
  });
});
