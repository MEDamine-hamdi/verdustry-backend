import xmlrpc.client

url = 'https://verdustry.odoo.com'
db = 'verdustry'
username = 'amie.bnr34@gmail.com'
api_key = 'ea46f0a06318f8931e80d95105ed673964037350'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, api_key, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

fields = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'fields_get',
    [],
    {'attributes': ['string', 'type']}
)

for name, meta in fields.items():
    if 'company' in name.lower():
        print(name, '-', meta.get('string'), '-', meta.get('type'))