import React, { useState } from "react";
import axios from "axios";

function App() {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState("");

  const executeCommand = async () => {
    const response = await axios.post("http://127.0.0.1:5000/execute_git", { command });
    setOutput(response.data.output || response.data.error);
  };

  return (
    <div>
      <h1>GitQuest: The Code Chronicles</h1>
      <input type="text" value={command} onChange={(e) => setCommand(e.target.value)} />
      <button onClick={executeCommand}>Run Command</button>
      <pre>{output}</pre>
    </div>
  );
}

export default App;
