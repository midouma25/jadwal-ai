import React from 'react';
import Navbar from './components/layout/Navbar';
import GeneratorWizard from './components/pages/GeneratorWizard';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 selection:bg-blue-200 pb-12">
      <Navbar />
      <GeneratorWizard />
    </div>
  );
}

export default App;