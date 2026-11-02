import { useEffect, useState } from "react";
import { api } from "../api";

export default function TaskList({ projectId }) {
  const [tasks, setTasks] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [title, setTitle] = useState("");
  const [filter, setFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    const qs = filter ? `&status=${filter}` : "";
    api(`/tasks/?project=${projectId}${qs}`)
      .then(data => { if (!cancelled) { setTasks(data.results); setStatus("ready"); } })
      .catch(err => { if (!cancelled) { setError(err); setStatus("error"); } });
    return () => { cancelled = true; };
  }, [projectId, filter]);

  async function addTask(e) {
    e.preventDefault();
    try {
      const created = await api("/tasks/", {
        method: "POST", body: { project: projectId, title },
      });
      setTasks(prev => [created, ...prev]);
      setTitle("");
      setError(null);
    } catch (err) {
      setError(err);
    }
  }

  async function toggleDone(task) {
    const next = task.status === "done" ? "todo" : "done";
    setTasks(prev => prev.map(t => (t.id === task.id ? { ...t, status: next } : t)));
    try {
      const updated = await api(`/tasks/${task.id}/`, { method: "PATCH", body: { status: next } });
      setTasks(prev => prev.map(t => (t.id === task.id ? updated : t)));
      setError(null);
    } catch (err) {
      setTasks(prev => prev.map(t => (t.id === task.id ? task : t)));
      setError(err);
    }
  }

  if (status === "loading") return <p>Loading…</p>;
  if (status === "error" && !tasks.length) {
    return <p role="alert">Could not load tasks ({error.status}).</p>;
  }

  return (
    <section>
      <form onSubmit={addTask}>
        <label htmlFor="new-task">New task </label>
        <input id="new-task" value={title} onChange={e => setTitle(e.target.value)} />
        <button disabled={title.trim().length < 3}>Add</button>
        {error?.data?.title && <p role="alert">{error.data.title[0]}</p>}
        {error?.data?.non_field_errors && <p role="alert">{error.data.non_field_errors[0]}</p>}
      </form>

      <label htmlFor="filter">Show </label>
      <select id="filter" value={filter} onChange={e => setFilter(e.target.value)}>
        <option value="">All</option>
        <option value="todo">To do</option>
        <option value="doing">In progress</option>
        <option value="done">Done</option>
      </select>

      {tasks.length === 0 ? (
        <p>No tasks yet.</p>
      ) : (
        <ul>
          {tasks.map(task => (
            <li key={task.id}>
              <input type="checkbox" checked={task.status === "done"}
                onChange={() => toggleDone(task)} aria-label={`Done: ${task.title}`} />
              {task.title} — {task.assignee_username ?? "Unassigned"}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}