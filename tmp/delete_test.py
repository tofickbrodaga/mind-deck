import requests, uuid, sys, subprocess, time
base='http://localhost:8000/api/v1'
email=f"test+{uuid.uuid4()}@example.com"
pw='pass1234'
s=requests.Session()
print('registering',email)
reg=s.post(f'{base}/users/register',json={'email':email,'username':'testuser','password':pw})
print('register',reg.status_code,reg.text)
login=s.post(f'{base}/users/login',json={'email':email,'password':pw})
print('login',login.status_code,login.text)
if login.status_code!=200:
    sys.exit(0)

token=login.json().get('access_token','')
print('token present:', bool(token))
headers={'Authorization':f'Bearer {token}'}

deck=s.post(f'{base}/decks',json={'title':'Test Deck','description':'For delete test'},headers=headers)
print('deck create',deck.status_code,deck.text)
if deck.status_code!=201:
    sys.exit(0)

deck_id=deck.json().get('id','')
print('deck_id',deck_id)

card=s.post(f'{base}/cards/deck/'+deck_id,json={'front':'Q','back':'A'},headers=headers)
print('card create',card.status_code,card.text)
if card.status_code!=201:
    sys.exit(0)

card_id=card.json().get('id','')
print('card_id',card_id)

delr=s.delete(f'{base}/cards/'+card_id,headers=headers)
print('delete',delr.status_code,delr.text)

print('\n-- app logs --\n')
print(subprocess.run(['docker-compose','logs','app','--tail=200'],capture_output=True,text=True).stdout)
