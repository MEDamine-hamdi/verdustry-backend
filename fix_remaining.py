import xmlrpc.client

url = 'https://verdustry.odoo.com'
db = 'verdustry'
username = 'amie.bnr34@gmail.com'
api_key = 'ea46f0a06318f8931e80d95105ed673964037350'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, api_key, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

for partner_id in [11, 12]:
    result = models.execute_kw(
        db, uid, api_key,
        'res.partner', 'write',
        [[partner_id], {'is_company': True}]
    )
    print(f'Updated id {partner_id}:', result)

check = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search_read',
    [[['is_company', '=', True]]],
    {'fields': ['name', 'is_company']}
)
print('Companies now:', check)