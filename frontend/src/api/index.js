import api from './client';

export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

export const valesAPI = {
  getAll: async (filters = {}) => {
    const response = await api.get('/vales', { params: filters });
    return response.data;
  },
  
  getOne: async (id) => {
    const response = await api.get(`/vales/${id}`);
    return response.data;
  },
  
  create: async (valeData) => {
    const response = await api.post('/vales', valeData);
    return response.data;
  },
  
  update: async (id, valeData) => {
    const response = await api.put(`/vales/${id}`, valeData);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/vales/${id}`);
    return response.data;
  },
};

export const productosAPI = {
  getAll: async () => {
    const response = await api.get('/productos');
    return response.data;
  },
  
  getOne: async (id) => {
    const response = await api.get(`/productos/${id}`);
    return response.data;
  },
  
  create: async (productoData) => {
    const response = await api.post('/productos', productoData);
    return response.data;
  },
  
  update: async (id, productoData) => {
    const response = await api.put(`/productos/${id}`, productoData);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/productos/${id}`);
    return response.data;
  },
};

export const dashboardAPI = {
  getConsumoHoy: async () => {
    const response = await api.get('/dashboard/consumo-hoy');
    return response.data;
  },
  
  getStockActual: async () => {
    const response = await api.get('/dashboard/stock-actual');
    return response.data;
  },
  
  getConsumo7Dias: async () => {
    const response = await api.get('/dashboard/consumo-7-dias');
    return response.data;
  },
  
  getConsumoSatelite7Dias: async () => {
    const response = await api.get('/dashboard/consumo-satelite-7-dias');
    return response.data;
  },
  
  getHistorico30Dias: async () => {
    const response = await api.get('/dashboard/historico-30-dias');
    return response.data;
  },
  
  getResumen: async () => {
    const response = await api.get('/dashboard/resumen');
    return response.data;
  },
};

export const reportesAPI = {
  getDiario: async () => {
    const response = await api.get('/reportes/diario');
    return response.data;
  },
  
  getSemanal: async () => {
    const response = await api.get('/reportes/semanal');
    return response.data;
  },
};
