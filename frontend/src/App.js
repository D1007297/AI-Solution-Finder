import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import SolutionLibrary from "./components/SolutionLibrary";
import Navbar from "./components/Navbar";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <BrowserRouter>
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/library" element={<SolutionLibrary />} />
          </Routes>
        </main>
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;