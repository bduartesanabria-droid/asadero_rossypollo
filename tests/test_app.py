from app.models import User, Prize


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Rossypollo Mundial' in response.data


def test_register_login_logout(client):
    response = client.post('/auth/register', data={
        'username': 'tester',
        'email': 'tester@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Bienvenido' in response.data or b'Bienvenido a Rossy Pollo' in response.data

    response = client.post('/auth/login', data={
        'username': 'tester',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Mi Panel' in response.data or b'Bienvenido' in response.data

    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Sesión cerrada exitosamente' in response.get_data(as_text=True)


def test_admin_prize_management(client, app):
    from app.models import db

    with app.app_context():
        admin = User(username='adminuser', email='admin@example.com', is_admin=True)
        admin.set_password('Password123!')
        db.session.add(admin)
        db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'adminuser',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Admin' in response.get_data(as_text=True)

    response = client.post('/admin/prize/new', data={
        'name': 'Premio Test',
        'description': 'Premio de prueba',
        'image_url': '',
        'phase': 'Final'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Premio creado exitosamente' in response.get_data(as_text=True)

    with app.app_context():
        prize = Prize.query.filter_by(name='Premio Test').first()
        assert prize is not None
        assert prize.phase == 'Final'
