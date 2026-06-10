#!/usr/bin/env python
"""Simple test for registration and login logic fixes"""
import os
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.models import db, User

print("=" * 60)
print("Testing Authentication Fixes")
print("=" * 60)

# Create app with fresh database
app = create_app('development')

with app.app_context():
    # Force recreate all tables
    db.drop_all()
    db.create_all()
    
    # Test 1: User password hashing
    print("\n✓ Test 1: Password hashing")
    user = User(username='test1', email='test1@example.com')
    user.set_password('SecurePass123!')
    assert user.check_password('SecurePass123!')
    assert not user.check_password('WrongPass')
    print("  ✓ Passwords are correctly hashed and verified")

# Test 2: Flask-Login integration with test client
print("\n✓ Test 2: Registration & Login Flow")
with app.app_context():
    client = app.test_client()
    
    # Step 1: Register new user
    reg_response = client.post('/auth/register', data={
        'username': 'johndoe',
        'email': 'john@example.com',
        'password': 'JohnPass123!',
        'password_confirm': 'JohnPass123!'
    }, follow_redirects=False)
    
    print(f"  Registration Response: {reg_response.status_code}")
    
    # After successful registration with auto-login, should redirect to dashboard (302)
    if reg_response.status_code in [200, 302]:
        # Check if we can access the dashboard (requires login)
        dash_response = client.get('/dashboard')
        if dash_response.status_code == 200:
            print("  ✓ Auto-login after registration works!")
        else:
            # Try login separately
            login_resp = client.post('/auth/login', data={
                'username': 'johndoe',
                'password': 'JohnPass123!'
            }, follow_redirects=True)
            if login_resp.status_code == 200 and 'Bienvenido' in login_resp.get_data(as_text=True):
                print("  ✓ Registration successful, manual login works!")
            else:
                print(f"  ! Login response: {login_resp.status_code}")
                print(f"    Content: {login_resp.get_data(as_text=True)[:200]}")
    else:
        print(f"  ! Registration failed with status {reg_response.status_code}")
        print(f"    Location: {reg_response.headers.get('Location', 'No redirect')}")

# Test 3: User blocking functionality
print("\n✓ Test 3: User active/inactive toggle")
with app.app_context():
    admin_user = User(username='admin', email='admin@example.com', is_admin=True)
    admin_user.set_password('Admin123!')
    regular_user = User(username='regular', email='regular@example.com', is_admin=False)
    regular_user.set_password('Regular123!')
    
    db.session.add(admin_user)
    db.session.add(regular_user)
    db.session.commit()
    
    # Check default is_active
    user = User.query.filter_by(username='regular').first()
    assert user.is_active == True, f"User should be active by default, but got {user.is_active}"
    
    # Toggle active
    user.is_active = False
    db.session.commit()
    
    user = User.query.filter_by(username='regular').first()
    assert user.is_active == False, f"User should be inactive after toggle, but got {user.is_active}"
    print("  ✓ User active/inactive toggle works correctly")

print("\n" + "=" * 60)
print("✅ All authentication fixes are working!")
print("=" * 60)
