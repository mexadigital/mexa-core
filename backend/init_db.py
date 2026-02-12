"""
Database initialization script
Creates initial data for MEXA application
"""
from app import create_app, db
from app.models.usuario import Usuario
from app.models.producto import Producto

def init_db():
    """Initialize database with seed data"""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if users already exist
        if Usuario.query.count() == 0:
            print("Creating initial users...")
            
            # Create admin user (Carlos)
            admin = Usuario(
                username='carlos',
                email='carlos@icafluor.com',
                password='admin123',  # Change in production!
                nombre_completo='Carlos - ICA FLUOR',
                rol='admin'
            )
            
            # Create regular user (Jefe)
            jefe = Usuario(
                username='jefe',
                email='jefe@icafluor.com',
                password='jefe123',  # Change in production!
                nombre_completo='Jefe - ICA FLUOR',
                rol='usuario'
            )
            
            db.session.add(admin)
            db.session.add(jefe)
            db.session.commit()
            print(f"✓ Created users: {admin.username}, {jefe.username}")
        
        # Check if products already exist
        if Producto.query.count() == 0:
            print("Creating initial products...")
            
            # EPP Products
            productos = [
                # Protección de cabeza
                Producto(nombre='Casco', descripcion='Casco de seguridad', categoria='EPP', unidad_medida='unidad', stock_minimo=20),
                
                # Protección de manos
                Producto(nombre='Guante de cuero', descripcion='Guante de cuero para trabajo pesado', categoria='EPP', unidad_medida='par', stock_minimo=30),
                Producto(nombre='Guante de latex', descripcion='Guante de latex desechable', categoria='EPP', unidad_medida='par', stock_minimo=50),
                Producto(nombre='Guante dieléctrico', descripcion='Guante para trabajo eléctrico', categoria='EPP', unidad_medida='par', stock_minimo=15),
                
                # Protección de pies
                Producto(nombre='Bota de seguridad', descripcion='Bota con punta de acero', categoria='EPP', unidad_medida='par', stock_minimo=25),
                Producto(nombre='Bota dieléctrica', descripcion='Bota aislante eléctrica', categoria='EPP', unidad_medida='par', stock_minimo=15),
                
                # Protección respiratoria
                Producto(nombre='Mascarilla N95', descripcion='Mascarilla respiratoria N95', categoria='EPP', unidad_medida='unidad', stock_minimo=100),
                Producto(nombre='Respirador con filtro', descripcion='Respirador de media cara con filtros', categoria='EPP', unidad_medida='unidad', stock_minimo=20),
                
                # Protección visual
                Producto(nombre='Lentes de seguridad', descripcion='Lentes de protección transparentes', categoria='EPP', unidad_medida='unidad', stock_minimo=30),
                Producto(nombre='Careta facial', descripcion='Careta de protección facial', categoria='EPP', unidad_medida='unidad', stock_minimo=20),
                
                # Protección auditiva
                Producto(nombre='Tapones auditivos', descripcion='Tapones desechables', categoria='EPP', unidad_medida='par', stock_minimo=100),
                Producto(nombre='Orejeras', descripcion='Orejeras de protección auditiva', categoria='EPP', unidad_medida='unidad', stock_minimo=20),
                
                # Protección de altura
                Producto(nombre='Arnés', descripcion='Arnés de seguridad para trabajo en altura', categoria='EPP', unidad_medida='unidad', stock_minimo=15),
                Producto(nombre='Línea de vida', descripcion='Línea de vida retráctil', categoria='EPP', unidad_medida='unidad', stock_minimo=10),
                
                # Ropa de protección
                Producto(nombre='Chaleco reflectante', descripcion='Chaleco de alta visibilidad', categoria='EPP', unidad_medida='unidad', stock_minimo=40),
                Producto(nombre='Overol', descripcion='Overol de trabajo', categoria='EPP', unidad_medida='unidad', stock_minimo=30),
                
                # Consumibles
                Producto(nombre='Disco de corte', descripcion='Disco de corte para amoladora 7"', categoria='Consumible', unidad_medida='unidad', stock_minimo=50),
                Producto(nombre='Disco de desbaste', descripcion='Disco de desbaste para amoladora 7"', categoria='Consumible', unidad_medida='unidad', stock_minimo=50),
                Producto(nombre='Electrodo 6011', descripcion='Electrodo para soldadura 6011', categoria='Consumible', unidad_medida='caja', stock_minimo=20),
                Producto(nombre='Cinta aislante', descripcion='Cinta aislante eléctrica', categoria='Consumible', unidad_medida='rollo', stock_minimo=30),
            ]
            
            for producto in productos:
                db.session.add(producto)
            
            db.session.commit()
            print(f"✓ Created {len(productos)} products")
        
        print("\n✅ Database initialized successfully!")
        print("\nDefault credentials:")
        print("Admin - Username: carlos, Password: admin123")
        print("User - Username: jefe, Password: jefe123")
        print("\n⚠️  IMPORTANT: Change these passwords in production!")


if __name__ == '__main__':
    init_db()
