import { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard({ refresh }) {
  const [consumoHoy, setConsumoHoy] = useState(null);
  const [stockActual, setStockActual] = useState([]);
  const [consumo7Dias, setConsumo7Dias] = useState(null);
  const [consumoSatelite, setConsumoSatelite] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [refresh]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [hoy, stock, dias, satelite] = await Promise.all([
        dashboardAPI.getConsumoHoy(),
        dashboardAPI.getStockActual(),
        dashboardAPI.getConsumo7Dias(),
        dashboardAPI.getConsumoSatelite7Dias(),
      ]);

      setConsumoHoy(hoy);
      setStockActual(stock);
      setConsumo7Dias(dias);
      setConsumoSatelite(satelite);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const disciplinaChartData = consumo7Dias ? {
    labels: consumo7Dias.dates.map(d => {
      const date = new Date(d);
      return date.toLocaleDateString('es-MX', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Civil',
        data: consumo7Dias.Civil,
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
      },
      {
        label: 'Mecánica',
        data: consumo7Dias.Mecánica,
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
      },
      {
        label: 'Eléctrica',
        data: consumo7Dias.Eléctrica,
        backgroundColor: 'rgba(251, 191, 36, 0.7)',
      },
    ],
  } : null;

  const sateliteChartData = consumoSatelite ? {
    labels: consumoSatelite.dates.map(d => {
      const date = new Date(d);
      return date.toLocaleDateString('es-MX', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Satélite #1',
        data: consumoSatelite['#1'],
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
      },
      {
        label: 'Satélite #2',
        data: consumoSatelite['#2'],
        backgroundColor: 'rgba(236, 72, 153, 0.7)',
      },
      {
        label: 'Satélite #3',
        data: consumoSatelite['#3'],
        backgroundColor: 'rgba(14, 165, 233, 0.7)',
      },
    ],
  } : null;

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-600">Cargando dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Consumo de Hoy */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-blue-50 border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Civil</h3>
          <p className="text-3xl font-bold text-blue-600">
            {consumoHoy?.Civil || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">unidades hoy</p>
        </div>

        <div className="card bg-green-50 border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Mecánica</h3>
          <p className="text-3xl font-bold text-green-600">
            {consumoHoy?.Mecánica || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">unidades hoy</p>
        </div>

        <div className="card bg-yellow-50 border-l-4 border-yellow-500">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Eléctrica</h3>
          <p className="text-3xl font-bold text-yellow-600">
            {consumoHoy?.Eléctrica || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">unidades hoy</p>
        </div>

        <div className="card bg-gray-50 border-l-4 border-gray-500">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Total</h3>
          <p className="text-3xl font-bold text-gray-700">
            {consumoHoy?.Total || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">unidades hoy</p>
        </div>
      </div>

      {/* Stock Actual */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Stock Actual</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {stockActual.slice(0, 9).map((item) => (
            <div
              key={item.producto_id}
              className={`p-3 rounded-lg border ${
                item.alerta
                  ? 'bg-red-50 border-red-200'
                  : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium text-gray-700">
                  {item.producto_nombre}
                </span>
                <span
                  className={`text-lg font-bold ${
                    item.alerta ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {item.stock_actual}
                </span>
              </div>
              {item.alerta && (
                <p className="text-xs text-red-600 mt-1">
                  ⚠️ Stock bajo (mínimo: {item.stock_minimo})
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Consumo por Disciplina (7 días)
          </h2>
          {disciplinaChartData && (
            <Bar data={disciplinaChartData} options={chartOptions} />
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Consumo por Satélite (7 días)
          </h2>
          {sateliteChartData && (
            <Bar data={sateliteChartData} options={chartOptions} />
          )}
        </div>
      </div>
    </div>
  );
}
