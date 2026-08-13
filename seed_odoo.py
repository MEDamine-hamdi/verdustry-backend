import xmlrpc.client

url = 'https://verdustry.odoo.com'
db = 'verdustry'
username = 'amie.bnr34@gmail.com'
api_key = 'ea46f0a06318f8931e80d95105ed673964037350'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, api_key, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

companies = [
    {'name': 'Acme Steel Ltd', 'is_company': True, 'country_id': 75},     # Germany
    {'name': 'Nordic Freight AB', 'is_company': True, 'country_id': 168}, # Sweden
    {'name': 'Sahara Metals SARL', 'is_company': True, 'country_id': 225},# Tunisia
]

for c in companies:
    new_id = models.execute_kw(db, uid, api_key, 'res.partner', 'create', [c])
    print(f"Created: {c['name']} -> id {new_id}")