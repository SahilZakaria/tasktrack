import TaskList from "./components/TaskList";

export default function App() {
  return (
    <main style={{ padding: 24 }}>
      <h1>TaskTrack</h1>
      <TaskList projectId={20} />
    </main>
  );
}