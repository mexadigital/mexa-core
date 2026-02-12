import { useState } from 'react';
import Header from '../components/Header';
import ValeForm from '../components/ValeForm';
import Dashboard from '../components/Dashboard';
import TablaHistorico from '../components/TablaHistorico';

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleValeCreated = () => {
    // Refresh dashboard and table when new vale is created
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard Principal
          </h1>
          <p className="text-gray-600">
            Gestión de EPP y Consumibles - ICA FLUOR
          </p>
        </div>

        <div className="space-y-8">
          {/* Form Section */}
          <ValeForm onSuccess={handleValeCreated} />

          {/* Dashboard Section */}
          <Dashboard refresh={refreshKey} />

          {/* Historical Table */}
          <TablaHistorico refresh={refreshKey} />
        </div>
      </main>
    </div>
  );
}
