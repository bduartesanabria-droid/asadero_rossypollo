from app import create_app  
app = create_app('development')  
client = app.test_client()  
resp = client.post('/auth/register', data={'username':'test2', 'email':'t2@t.com', 'password':'pass', 'password_confirm':'pass'}, follow_redirects=True)  
print(resp.data.decode('utf-8'))  
