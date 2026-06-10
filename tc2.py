import urllib.request, urllib.parse  
data = urllib.parse.urlencode({'username':'t6','email':'t6@t.com','password':'pass','password_confirm':'pass'}).encode()  
req = urllib.request.Request('http://127.0.0.1:5000/auth/register', data=data)  
print(urllib.request.urlopen(req).getcode())  
