import Header from '../components/Header';

export default function Reportes() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Reportes
          </h1>
          <p className="text-gray-600">
            Reportes automáticos diarios y semanales
          </p>
        </div>

        <div className="card">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              Reportes en Desarrollo
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              La generación automática de reportes diarios y semanales se implementará en la Fase 2.
              Por ahora puedes ver el histórico en el dashboard principal.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
