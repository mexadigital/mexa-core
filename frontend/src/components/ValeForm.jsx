import { useState, useEffect } from 'react';
import { valesAPI, productosAPI } from '../api';

export default function ValeForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    producto_id: '',
    disciplina: '',
    satelite: '',
    cantidad_salida: '',
    stock_actual: '',
    observaciones: '',
  });
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const disciplinas = ['Civil', 'Mecánica', 'Eléctrica'];
  const satelites = ['#1', '#2', '#3'];

  useEffect(() => {
    loadProductos();
  }, []);

  const loadProductos = async () => {
    try {
      const data = await productosAPI.getAll();
      setProductos(data);
    } catch (err) {
      console.error('Error loading productos:', err);
      setError('Error al cargar productos');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Validate form
      if (!formData.producto_id || !formData.disciplina || !formData.satelite ||
          !formData.cantidad_salida || !formData.stock_actual) {
        setError('Por favor complete todos los campos requeridos');
        setLoading(false);
        return;
      }

      // Create vale
      await valesAPI.create({
        producto_id: parseInt(formData.producto_id),
        disciplina: formData.disciplina,
        satelite: formData.satelite,
        cantidad_salida: parseInt(formData.cantidad_salida),
        stock_actual: parseInt(formData.stock_actual),
        observaciones: formData.observaciones || null,
      });

      setSuccess('Vale registrado exitosamente');
      
      // Reset form
      setFormData({
        producto_id: '',
        disciplina: '',
        satelite: '',
        cantidad_salida: '',
        stock_actual: '',
        observaciones: '',
      });

      // Call success callback
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      console.error('Error creating vale:', err);
      setError(err.response?.data?.error || 'Error al registrar vale');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Registrar Vale Digital
      </h2>

      {error && (
        <div className="alert alert-error mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success mb-4">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">
              Disciplina <span className="text-red-500">*</span>
            </label>
            <select
              name="disciplina"
              value={formData.disciplina}
              onChange={handleChange}
              className="input"
              required
            >
              <option value="">Seleccione disciplina</option>
              {disciplinas.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">
              Satélite <span className="text-red-500">*</span>
            </label>
            <select
              name="satelite"
              value={formData.satelite}
              onChange={handleChange}
              className="input"
              required
            >
              <option value="">Seleccione satélite</option>
              {satelites.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="label">
              Producto <span className="text-red-500">*</span>
            </label>
            <select
              name="producto_id"
              value={formData.producto_id}
              onChange={handleChange}
              className="input"
              required
            >
              <option value="">Seleccione producto</option>
              {productos.map(p => (
                <option key={p.id} value={p.id}>
                  {p.nombre} ({p.categoria})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">
              Cantidad Salida <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="cantidad_salida"
              value={formData.cantidad_salida}
              onChange={handleChange}
              className="input"
              min="0"
              required
            />
          </div>

          <div>
            <label className="label">
              Stock Actual <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="stock_actual"
              value={formData.stock_actual}
              onChange={handleChange}
              className="input"
              min="0"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="label">
              Observaciones
            </label>
            <textarea
              name="observaciones"
              value={formData.observaciones}
              onChange={handleChange}
              className="input"
              rows="3"
              placeholder="Notas adicionales (opcional)"
            />
          </div>
        </div>

        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Guardando...' : 'Guardar Reporte Diario'}
          </button>
        </div>
      </form>
    </div>
  );
}
