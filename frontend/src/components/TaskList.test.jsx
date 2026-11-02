import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TaskList from "./TaskList";

const mocks = vi.hoisted(() => ({ impl: null }));

vi.mock("../api", () => ({
  api: (...args) => mocks.impl(...args),
}));

describe("TaskList", () => {
  beforeEach(() => {
    mocks.impl = null;
  });

  it("renders tasks from the API", async () => {
    mocks.impl = () =>
      Promise.resolve({
        results: [{ id: 1, title: "Write docs", status: "todo", assignee_username: null }],
      });
    render(<TaskList projectId={20} />);
    expect(await screen.findByText(/Write docs/)).toBeInTheDocument();
  });

  it("shows an error when the API fails", async () => {
    mocks.impl = () =>
      Promise.reject(Object.assign(new Error("Server error"), { status: 500 }));
    render(<TaskList projectId={20} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not load tasks (500).");
  });

  it("shows an empty state", async () => {
    mocks.impl = () => Promise.resolve({ results: [] });
    render(<TaskList projectId={20} />);
    expect(await screen.findByText("No tasks yet.")).toBeInTheDocument();
  });
});