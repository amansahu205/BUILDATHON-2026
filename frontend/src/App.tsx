import { useState } from "react";
import CaseSelector from "./components/CaseSelector";
import DepositionSession from "./components/DepositionSession";
import cases from "./cases";
import type { VerdictCase } from "./types";
import "./App.css";

function App() {
  const [activeCase, setActiveCase] = useState<VerdictCase | null>(null);

  if (activeCase) {
    return (
      <DepositionSession
        activeCase={activeCase}
        onEnd={() => setActiveCase(null)}
      />
    );
  }

  return <CaseSelector cases={cases} onSelect={setActiveCase} />;
}

export default App;
