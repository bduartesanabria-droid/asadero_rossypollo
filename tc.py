import requests  
r = requests.post('http://127.0.0.1:5000/auth/register', data={'username':'t5','email':'t5@t.com','password':'pass','password_confirm':'pass'})  
print(r.status_code)  
