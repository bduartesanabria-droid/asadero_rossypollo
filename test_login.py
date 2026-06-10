from app import create_app  
app = create_app('development')  
client = app.test_client()  
resp = client.get('/auth/login')  
print(resp.status_code)  
