import json

with open('d:/ibm/p2p/members_data.json', 'r', encoding='utf-8') as f:
    js_data = f.read()

with open('d:/ibm/p2p/member_lookup_template.html', 'r', encoding='utf-8') as f:
    template = f.read()

full_html = template.replace('__MEMBERS_DATA__', js_data)

with open('d:/ibm/p2p/member_lookup.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print('Done! member_lookup.html created')
print('File size:', len(full_html), 'chars')
