"""
Multi-tenant database models - importable wrapper
"""
from flask import current_app

# Lazy-loaded model references
_models_cache = {}

def _get_model(name):
    """Get model class from current app context"""
    if name not in _models_cache:
        _models_cache[name] = current_app.models[name]
    return _models_cache[name]

# Create lazy properties for each model
class ModelProxy:
    @property
    def Tenant(self):
        return _get_model('Tenant')
    
    @property
    def Usuario(self):
        return _get_model('Usuario')
    
    @property
    def Producto(self):
        return _get_model('Producto')
    
    @property
    def Vale(self):
        return _get_model('Vale')
    
    @property
    def AuditLog(self):
        return _get_model('AuditLog')

models = ModelProxy()

# Export individual references for convenience
Tenant = property(lambda self: models.Tenant)
Usuario = property(lambda self: models.Usuario)
Producto = property(lambda self: models.Producto)
Vale = property(lambda self: models.Vale)
AuditLog = property(lambda self: models.AuditLog)
