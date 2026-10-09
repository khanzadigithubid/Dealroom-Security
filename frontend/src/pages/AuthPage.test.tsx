import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { getToken } from "../api";
import AuthPage from "./AuthPage";

function jsonResponse(status: number, body: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => body,
  } as unknown as Response;
}

async function fillRegisterForm() {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Full name"), "Alex Khan");
  await user.type(screen.getByLabelText("Company"), "Acme SaaS Inc.");
  await user.type(screen.getByLabelText("Email"), "alex@acme.com");
  await user.type(screen.getByLabelText("Password"), "password123");
  return user;
}

describe("AuthPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("stores the token on a successful registration", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { access_token: "tok-123" }));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    );
    const user = await fillRegisterForm();
    await user.click(screen.getByRole("button", { name: "Create workspace" }));

    await waitFor(() => expect(getToken()).toBe("tok-123"));
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/register", expect.objectContaining({ method: "POST" }));
  });

  it("shows a readable message when the API returns validation errors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(422, {
        detail: [
          {
            type: "string_too_short",
            loc: ["body", "company_name"],
            msg: "String should have at least 2 characters",
            ctx: { min_length: 2 },
          },
        ],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    );
    const user = await fillRegisterForm();
    await user.click(screen.getByRole("button", { name: "Create workspace" }));

    expect(await screen.findByText("Company must be at least 2 characters")).toBeInTheDocument();
    expect(getToken()).toBeNull();
  });

  it("blocks submission when the email domain is missing a dot", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    );
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Full name"), "Alex");
    await user.type(screen.getByLabelText("Company"), "Acme");
    await user.type(screen.getByLabelText("Email"), "alex@acme");
    await user.type(screen.getByLabelText("Password"), "password123");
    await user.click(screen.getByRole("button", { name: "Create workspace" }));

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
