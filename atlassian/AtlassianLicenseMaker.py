import base64
import sys
import struct
import zlib

from Crypto.Hash import SHA
from Crypto.PublicKey import DSA
from Crypto.Util import asn1
from Crypto.Util import number
from Crypto.Random import random


demoLicense = b'AAABBw0ODAoPeNptkFtLxDAQhd/zKwI+R9Kwy66FPKxthGhvtF0p4kuso0a6sUwvuP/edissyj4MDHPOfHOYqzu0tICWeoJy4a+FzzkNwpIK7q1ICF2Ntu3tl5P3Ot89+1SNphnMPCEBwqkJTQ9y9jN+wzxBPi2a68jW4DpQr/a0rZJS5VmuC0XOBNnjAH/s5bGFxBxABmkcqzzQu2jRTd3bEZaFZvE+AnYzRJDYWNeDM64G9d1aPJ4TeXxOlOK7cbZbjrbNgkyGwwtg+rbvJpBkHikAR0Adytt0XzFV7R5Y+qQzVkWZIoVK5FQsWq03YrvdkN/Ekz3S4SXlcpRswPrDdPD/aT+P1nzDMC0CFQCM9+0LlHVNnZQnSTwuRO3eK+2gVgIUCteTs4Q3khIgrnsY64hxYB/d8bM='
demoKeys = b'MIIBuDCCASwGByqGSM44BAEwggEfAoGBAP1/U4EddRIpUt9KnC7s5Of2EbdSPO9EAMMeP4C2USZpRV1AIlH7WT2NWPq/xfW6MPbLm1Vs14E7gB00b/JmYLdrmVClpJ+f6AR7ECLCT7up1/63xhv4O1fnxqimFQ8E+4P208UewwI1VBNaFpEy9nXzrith1yrv8iIDGZ3RSAHHAhUAl2BQjxUjC8yykrmCouuEC/BYHPUCgYEA9+GghdabPd7LvKtcNrhXuXmUr7v6OuqC+VdMCz0HgmdRWVeOutRZT+ZxBxCBgLRJFnEj6EwoFhO3zwkyjMim4TwWeotUfI0o4KOuHiuzpnWRbqN/C/ohNWLx+2J6ASQ7zKTxvqhRkImog9/hWuWfBpKLZl6Ae1UlZAFMO/7PSSoDgYUAAoGBAIvfweZvmGo5otwawI3no7Udanxal3hX2haw962KL/nHQrnC4FG2PvUFf34OecSK1KtHDPQoSQ+DHrfdf6vKUJphw0Kn3gXm4LS8VK/LrY7on/wh2iUobS2XlhuIqEc5mLAUu9Hd+1qxsQkQ50d0lzKrnDqPsM0WA9htkdJJw2nS'
prefixs = struct.pack('BBBBB', 13, 14, 12, 10, 15)

'''
license_text = \'''#Fri Sep 12 02:52:00 CDT 2014
Description=JIRA: COMMERCIAL
CreationDate=2014-09-12
jira.LicenseEdition=ENTERPRISE
Evaluation=false
jira.LicenseTypeName=COMMERCIAL
jira.active=true
licenseVersion=2
MaintenanceExpiryDate=2099-10-12
Organisation=ti
jira.NumberOfUsers=-1
ServerID=B1IX-MYA7-6QEP-8K00
SEN=SEN-L4572887
LicenseID=LIDSEN-L4572887
LicenseExpiryDate=2099-10-12
PurchaseDate=2014-09-12'''


def getLicenseContent(licenseBytes):
    sig_len, = struct.unpack('>I', licenseBytes[:4])
    fmt = '%ds%ds' % (sig_len, len(licenseBytes) - sig_len - 4)
    sig, hash = struct.unpack(fmt, licenseBytes[4:])
    return sig, hash


def load_dsa_key(pub_key):
    der = base64.b64decode(pub_key)

    cert = asn1.DerSequence()
    cert.decode(der)

    y_asn = asn1.DerInteger()
    y_asn.decode(cert[1][4:])
    y = y_asn.value

    pubkeyInfo = asn1.DerSequence()
    pubkeyInfo.decode(cert[0])

    pubkeys = asn1.DerSequence()
    pubkeys.decode(pubkeyInfo[1])
    p, q, g = pubkeys[:]

    return DSA.construct((y, g, p, q))


def gen_dsa_pub_key(dsa_key, old_key):

    der = base64.b64decode(old_key)

    cert = asn1.DerSequence()
    cert.decode(der)

    y_asn = asn1.DerInteger()
    y_asn.decode(cert[1][4:])
    y = y_asn.value

    pubkeyInfo = asn1.DerSequence()
    pubkeyInfo.decode(cert[0])

    pubkeys = asn1.DerSequence()
    pubkeys[:] = [dsa_key.p, dsa_key.q, dsa_key.g]

    pubkeyInfo[1] = pubkeys.encode()

    y_asn = asn1.DerInteger(dsa_key.y).encode()
    y_asn_prefix = struct.pack('BBBB', 3, 0x81, len(y_asn) + 1, 0)
    cert[:] = [pubkeyInfo.encode(), y_asn_prefix + y_asn]

    return base64.b64encode(cert.encode())


def gen_default_dsa_key():
    y = 10065689456240776697243340416224367304785334515903313938753754692449556744891294275571921504812155755633033070842442588494918706471482430570053177445644851409815983894470226083940844477850160279070472918743069426277569357040310205734636800470656967025557907735225590493033003364020999812910619036024526885174
    x = 421795802289395826330823439675135199394937484571
    p = 89884656743115803759180203114063383466180690588722053911463224944885017434174903858634611545540835526658396218743967959201220771129990761195103857796657133483888273939088694871893945049965573302513381214518927077553282692268109694520931555898962816380021211527704558026558765695609946702501030536821136113329
    q = 755719585439660880181233694028045355865479263581
    g = 3858849187684168834100460213688488364714152124092208039472479785767018518758411189129858105331022159237787752225919238451049099638627854779720795529639191345479493879067880151209974626184020193962141724836702547632962279245016730666514536955424657022187744035456419806555119892163419599934826518566694719935

    return DSA.construct((y, g, p, q, x))


def dsa_verify_demo():
    from Crypto.Random import random
    from Crypto.PublicKey import DSA
    from Crypto.Hash import SHA

    message = b"Hello"
    key = DSA.generate(1024)
    h = SHA.new(message).digest()
    k = random.StrongRandom().randint(1, key.q-1)
    sig = key.sign(h, k)
    print(h)
    print(sig)
    if key.verify(h, sig):
        print("OK")
    else:
        print("Incorrect signature")


def int2_fmt(value, mod):
    out = ''

    if value == 0:
        out = '0'
    else:
        def l_mod(a): return chr((a % mod) + ord('0')) if (a %
                                                           mod < 10) else chr((a % mod) - 10 + ord('a'))
        while(value > 0):
            out = l_mod(value) + out
            value = int(value / mod)

    return out


def gen_license(message, key):
    content = prefixs + zlib.compress(message.encode(encoding='utf_8'))
    h = SHA.new(content).digest()
    k = random.StrongRandom().randint(1, key.q-1)
    sig = key.sign(h, k)

    sig_der = asn1.DerSequence()
    sig_der[:] = [sig[0], sig[1]]
    sig_part = sig_der.encode()

    len_part = struct.pack('>I', len(content))

    concate_license = base64.b64encode(len_part + content + sig_part)

    license = concate_license + \
        ('X02' + int2_fmt(len(concate_license), 31)).encode('utf-8')
    return (license)


def test_old_license():
    demoBytes = base64.b64decode(demoLicense)

    content, sig_content = getLicenseContent(demoBytes)

    sig_der = asn1.DerSequence()
    sig_der.decode(sig_content)
    sig = (sig_der[0], sig_der[1])

    key = load_dsa_key(demoKeys)
    h = SHA.new(content).digest()

    if key.verify(h, sig):
        print("OK")
    else:
        print("Incorrect signature")


def read_license_from_file(fname):
    with open(fname) as f:
        data = f.read()

    return data


def main():
    key = gen_default_dsa_key()
    pub_key = gen_dsa_pub_key(key, demoKeys)
    print('===Print public key:===')
    print(pub_key)

    fname = 'jira.lic' if len(sys.argv) == 1 else sys.argv[1]
    print('\n===Generate license for "%s":===' % fname)
    license_text = read_license_from_file(fname)

    jira_license = gen_license(license_text, key)
    print(jira_license)


if __name__ == '__main__':
    main()
