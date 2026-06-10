from app import create_app  
app = create_app('development')  
client = app.test_client()  
resp = client.post('/auth/register', data={'username':'test1', 'email':'t1@t.com', 'password':'pass', 'password_confirm':'pass'})  
print(resp.status_code)  
