import string
import jinja2
import yaml


def ldifcreator(sn, givenName, dc1, dc2, emaildomain):
    s = '''
version: 1

dn: cn={{p.sn | capitalize}} {{p.givenName | capitalize}},ou=users,dc={{dc1}},dc={{dc2}}
cn: {{p.sn | capitalize}} {{p.givenName | capitalize}}
givenname: {{p.givenName | capitalize}}
mail: {{p.sn | lower}}{{p.givenName | lower}}@{{emaildomain}}
objectclass: inetOrgPerson
objectclass: top
sn: {{p.sn | capitalize}}
uid: {{p.sn | lower}}{{p.givenName | lower}}
# userpassword: 123456
userpassword: {MD5}4QrcOUm6Wau+VuBX8g+IPg==
'''

    t = jinja2.Template(s)
    return t.render(p={
        "sn": sn,
        "givenName": givenName,
    }, dc1=dc1, dc2=dc2, emaildomain=emaildomain)


def main():

    users = [
        "li hao",
        "wang min",
    ]

    for u in users:
        sn, givenName = u.split()
        o = ldifcreator(sn,  givenName, "example", "org", "example.org")

        with open("%s%s.ldif" % (sn, givenName), "wb") as f:
            f.write(o.encode('utf8'))


if __name__ == "__main__":
    main()
