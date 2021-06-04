import ldap
import ldap.modlist as modlist
import base64, sys


l = ldap.initialize('ldap://10.117.2.135')

l.simple_bind_s('INSTENV\Administrator','P[dsWEDfJC4Bt=8Vf4cCsM2e')


name = "name"
second_name = "secondname"
fullname = name + " " + second_name
mail = "name_secondname@company.com"
company_id = "id1234"
password = "passsword"

base_dn = "ou=TestUsers,dc=smoroz7,dc=local"
user_dn = 'CN=' + name + ' '  + second_name + ',' + base_dn

user_attrs = {}
user_attrs['objectclass'] = ['top', 'person', 'organizationalPerson', 'user']
user_attrs['cn'] = fullname
user_attrs['givenName'] = str(name)
user_attrs['sn'] = str(second_name)
user_attrs['displayName'] = "%s" % fullname
user_attrs['mail'] = mail
user_ldif = modlist.addModlist(user_attrs)


add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password])]
# 512 will set user account to enabled
mod_acct = [(ldap.MOD_REPLACE, 'userAccountControl', '512')]


l.add_s(user_dn, user_ldif)
l.modify_s(user_dn, add_pass)
l.modify_s(user_dn, mod_acct)

