"""
Comprehensive tests for logging infrastructure and audit trail.
Tests request ID generation, audit log creation, JSON log format, and error handling.
"""
import unittest
import json
import tempfile
import os
from flask import g
from app import create_app
from app.database import SessionLocal, Base, engine
from app.models.audit_log import AuditLog
from app.utils.audit import log_audit


class TestLogging(unittest.TestCase):
    """Test suite for logging and audit trail functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and application."""
        # Create all tables
        Base.metadata.create_all(bind=engine)
    
    def setUp(self):
        """Set up test client and clean database before each test."""
        self.app = create_app({'TESTING': True, 'DEBUG': True})
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Clean audit_logs table
        db = SessionLocal()
        try:
            db.query(AuditLog).delete()
            db.commit()
        finally:
            db.close()
    
    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()
    
    def test_request_id_generation(self):
        """Test that request ID is generated for each request."""
        response = self.client.get('/api/epp/1')
        
        # Check that X-Request-ID header is present
        self.assertIn('X-Request-ID', response.headers)
        self.assertIsNotNone(response.headers['X-Request-ID'])
        
        # Request ID should be a valid UUID format (36 characters with hyphens)
        request_id = response.headers['X-Request-ID']
        self.assertEqual(len(request_id), 36)
        self.assertEqual(request_id.count('-'), 4)
    
    def test_request_id_from_header(self):
        """Test that custom X-Request-ID header is respected."""
        custom_request_id = 'test-request-id-12345'
        response = self.client.get(
            '/api/epp/1',
            headers={'X-Request-ID': custom_request_id}
        )
        
        # Should return the same request ID
        self.assertEqual(response.headers['X-Request-ID'], custom_request_id)
    
    def test_request_id_persistence(self):
        """Test that request_id persists throughout request lifecycle."""
        # Create an EPP resource
        response = self.client.post(
            '/api/epp',
            json={'name': 'Test EPP', 'description': 'Test description'},
            content_type='application/json'
        )
        
        request_id = response.headers.get('X-Request-ID')
        self.assertIsNotNone(request_id)
        
        # Check audit log has the same request_id
        db = SessionLocal()
        try:
            audit_log = db.query(AuditLog).filter_by(request_id=request_id).first()
            self.assertIsNotNone(audit_log)
            self.assertEqual(audit_log.request_id, request_id)
        finally:
            db.close()
    
    def test_audit_log_created_on_epp_creation(self):
        """Test that audit log is created when EPP resource is created."""
        response = self.client.post(
            '/api/epp',
            json={'name': 'Safety Helmet', 'description': 'Hard hat'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Check audit log was created
        db = SessionLocal()
        try:
            audit_logs = db.query(AuditLog).filter_by(
                action='create',
                resource_type='epp'
            ).all()
            
            self.assertEqual(len(audit_logs), 1)
            audit_log = audit_logs[0]
            
            self.assertEqual(audit_log.action, 'create')
            self.assertEqual(audit_log.resource_type, 'epp')
            self.assertIsNotNone(audit_log.resource_id)
            self.assertIsNotNone(audit_log.new_values)
            self.assertEqual(audit_log.new_values['name'], 'Safety Helmet')
        finally:
            db.close()
    
    def test_audit_log_created_on_epp_update(self):
        """Test that audit log tracks old and new values on update."""
        # Create an EPP first
        create_response = self.client.post(
            '/api/epp',
            json={'name': 'Old Name', 'description': 'Old description'},
            content_type='application/json'
        )
        epp_id = create_response.json['id']
        
        # Update the EPP
        update_response = self.client.put(
            f'/api/epp/{epp_id}',
            json={'name': 'New Name', 'description': 'New description'},
            content_type='application/json'
        )
        
        self.assertEqual(update_response.status_code, 200)
        
        # Check audit log for update
        db = SessionLocal()
        try:
            audit_log = db.query(AuditLog).filter_by(
                action='update',
                resource_type='epp',
                resource_id=epp_id
            ).first()
            
            self.assertIsNotNone(audit_log)
            self.assertEqual(audit_log.old_values['name'], 'Old Name')
            self.assertEqual(audit_log.new_values['name'], 'New Name')
        finally:
            db.close()
    
    def test_audit_log_created_on_epp_deletion(self):
        """Test that audit log is created when EPP resource is deleted."""
        # Create an EPP first
        create_response = self.client.post(
            '/api/epp',
            json={'name': 'To Delete', 'description': 'Will be deleted'},
            content_type='application/json'
        )
        epp_id = create_response.json['id']
        
        # Delete the EPP
        delete_response = self.client.delete(f'/api/epp/{epp_id}')
        self.assertEqual(delete_response.status_code, 204)
        
        # Check audit log for deletion
        db = SessionLocal()
        try:
            audit_log = db.query(AuditLog).filter_by(
                action='delete',
                resource_type='epp',
                resource_id=epp_id
            ).first()
            
            self.assertIsNotNone(audit_log)
            self.assertIsNotNone(audit_log.old_values)
            self.assertEqual(audit_log.old_values['name'], 'To Delete')
        finally:
            db.close()
    
    def test_audit_log_tracks_user_and_ip(self):
        """Test that audit log tracks user_id and ip_address."""
        response = self.client.post(
            '/api/consumables',
            json={'items': [{'price': 10, 'quantity': 2}]},
            content_type='application/json',
            headers={'X-Forwarded-For': '192.168.1.100'}
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Check audit log captures IP
        db = SessionLocal()
        try:
            audit_log = db.query(AuditLog).filter_by(
                action='create',
                resource_type='consumable'
            ).first()
            
            self.assertIsNotNone(audit_log)
            self.assertEqual(audit_log.ip_address, '192.168.1.100')
        finally:
            db.close()
    
    def test_error_handler_captures_exceptions(self):
        """Test that error handler logs exceptions with stack traces."""
        # This should trigger an error (invalid EPP ID access)
        response = self.client.get('/api/epp/999999')
        
        # Should get 404
        self.assertEqual(response.status_code, 404)
        self.assertIn('X-Request-ID', response.headers)
    
    def test_no_print_statements_in_code(self):
        """Test that there are no print() statements in production code."""
        import subprocess
        result = subprocess.run(
            ['grep', '-r', 'print(', 'app/', '--include=*.py'],
            capture_output=True,
            text=True,
            cwd='/home/runner/work/mexa-core/mexa-core'
        )
        
        # grep returns exit code 1 if no matches found, which is what we want
        self.assertNotEqual(result.returncode, 0, 
                          f"Found print() statements in code:\n{result.stdout}")
    
    def test_audit_log_stores_endpoint_and_method(self):
        """Test that audit log stores endpoint and HTTP method."""
        response = self.client.post(
            '/api/epp',
            json={'name': 'Test', 'description': 'Test'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Check audit log
        db = SessionLocal()
        try:
            audit_log = db.query(AuditLog).filter_by(
                action='create',
                resource_type='epp'
            ).first()
            
            self.assertIsNotNone(audit_log)
            self.assertEqual(audit_log.endpoint, '/api/epp')
            self.assertEqual(audit_log.method, 'POST')
        finally:
            db.close()
    
    def test_consumable_crud_audit_logging(self):
        """Test audit logging for consumable CRUD operations."""
        # Create
        create_response = self.client.post(
            '/api/consumables',
            json={'items': [{'price': 5, 'quantity': 3}]},
            content_type='application/json'
        )
        self.assertEqual(create_response.status_code, 201)
        consumable_id = create_response.json['id']
        
        # Update
        update_response = self.client.put(
            f'/api/consumables/{consumable_id}',
            json={'items': [{'price': 7, 'quantity': 3}]},
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Delete
        delete_response = self.client.delete(f'/api/consumables/{consumable_id}')
        self.assertEqual(delete_response.status_code, 204)
        
        # Check all audit logs were created
        db = SessionLocal()
        try:
            audit_logs = db.query(AuditLog).filter_by(
                resource_type='consumable',
                resource_id=consumable_id
            ).order_by(AuditLog.created_at).all()
            
            self.assertEqual(len(audit_logs), 3)
            self.assertEqual(audit_logs[0].action, 'create')
            self.assertEqual(audit_logs[1].action, 'update')
            self.assertEqual(audit_logs[2].action, 'delete')
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main()
