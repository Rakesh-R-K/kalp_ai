import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./layouts/Layout";
import Home from "./pages/Home";
import Capture from "./pages/Capture";
import Memory from "./pages/Memory";
import Reasoning from "./pages/Reasoning";
import CustomCursor from "./components/CustomCursor";

import "./App.css";

function App() {
  return (
    <Router>
      <CustomCursor />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="capture" element={<Capture />} />
          <Route path="memory" element={<Memory />} />
          <Route path="reasoning" element={<Reasoning />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
