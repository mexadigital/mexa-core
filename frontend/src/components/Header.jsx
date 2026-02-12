import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              MEXA
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link
                to="/"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/reportes"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Reportes
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <span className="text-gray-600">Hola, </span>
              <span className="font-medium text-gray-900">{user?.username}</span>
              {user?.rol === 'admin' && (
                <span className="ml-2 px-2 py-1 text-xs bg-primary-100 text-primary-700 rounded">
                  Admin
                </span>
              )}
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
