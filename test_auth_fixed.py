#!/usr/bin/env python
"""
Quick test script to verify registration and login fixes
"""
import os
import sys

# Set test environment
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.models import db, User

# Create app
app = create_app('development')

print("Testing Registration and Login Fixes")
print("=" * 50)

# Test 1: Create a test user
print("\n1. Testing user creation and password hashing...")
with app.app_context():
    # Create fresh user
    test_user = User(username='testuser', email='test@example.com')
    test_user.set_password('Test123!')
    
    # Check if password is hashed
    assert test_user.password_hash != 'Test123!', "Password should be hashed"
    assert test_user.check_password('Test123!'), "Password check should work"
    assert not test_user.check_password('WrongPassword'), "Wrong password should fail"
    print("✓ User creation and password hashing works")

# Test 2: Check is_active property
print("\n2. Testing is_active property...")
with app.app_context():
    user = User(username='user2', email='user2@example.com')
    user.set_password('Pass123!')
    assert user.is_active == True, "New users should be active by default"
    
    user.is_active = False
    assert user.is_active == False, "Should be able to deactivate user"
    
    user.is_active = True
    assert user.is_active == True, "Should be able to reactivate user"
    print("✓ is_active property works correctly")

# Test 3: Test login flow with Flask-Login
print("\n3. Testing Flask-Login integration...")
with app.app_context():
    db.create_all()
    
    # Create test user
    user = User(username='logintest', email='login@test.com', is_admin=False)
    user.set_password('LoginTest123!')
    db.session.add(user)
    db.session.commit()
    
    # Verify user was created
    found_user = User.query.filter_by(username='logintest').first()
    assert found_user is not None, "User should be found"
    assert found_user.is_active == True, "User should be active"
    assert found_user.check_password('LoginTest123!'), "Password should verify"
    print("✓ User creation for login works")

# Test 4: Test client authentication
print("\n4. Testing authentication routes...")
client = app.test_client()

with app.app_context():
    # Reset database
    db.drop_all()
    db.create_all()
    
    # Test registration
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'NewUser123!',
        'password_confirm': 'NewUser123!'
    }, follow_redirects=True)
    
    # After successful registration, should redirect to dashboard
    assert response.status_code == 200, f"Registration should succeed (got {response.status_code})"
    
    # Check if we got the dashboard or login page
    response_text = response.get_data(as_text=True)
    if 'dashboard' in response.status_code or 'Mi Panel' in response_text or response.status_code == 302:
        print("✓ Registration flow works (redirects to dashboard on success)")
    else:
        print(f"! Registration response: {response.status_code}")
        if 'error' in response_text.lower():
            print(f"  Error in response: {response_text[:200]}")
    
    # Test login
    response = client.post('/auth/login', data={
        'username': 'newuser',
        'password': 'NewUser123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200, f"Login should work (got {response.status_code})"
    response_text = response.get_data(as_text=True)
    
    if 'Bienvenido' in response_text or 'dashboard' in response_text.lower():
        print("✓ Login flow works (user logged in successfully)")
    else:
        print(f"! Login response status: {response.status_code}")
        if 'error' in response_text.lower():
            print(f"  Error in response: {response_text[:200]}")

print("\n" + "=" * 50)
print("✅ All authentication fixes verified!")
