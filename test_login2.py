from app import create_app  
app = create_app('development')  
client = app.test_client()  
resp = client.post('/auth/login', data={'username':'test2', 'password':'pass'})  
print(resp.status_code)  
