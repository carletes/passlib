"""passlib.hash.mysql

MySQL 3.2.3 / OLD_PASSWORD()

    This implements Mysql's OLD_PASSWORD algorithm, introduced in version 3.2.3, deprecated in version 4.1.

    See :mod:`passlib.hash.mysql_41` for the new algorithm was put in place in version 4.1

    This algorithm is known to be very insecure, and should only be used to verify existing password hashes.

    http://djangosnippets.org/snippets/1508/

MySQL 4.1.1 / NEW PASSWORD
    This implements Mysql new PASSWORD algorithm, introduced in version 4.1.

    This function is unsalted, and therefore not very secure against rainbow attacks.
    It should only be used when dealing with mysql passwords,
    for all other purposes, you should use a salted hash function.

    Description taken from http://dev.mysql.com/doc/refman/6.0/en/password-hashing.html
"""
#=========================================================
#imports
#=========================================================
#core
import re
import logging; log = logging.getLogger(__name__)
from warnings import warn
#site
#libs
#pkg
from passlib.base import register_crypt_handler
from passlib.utils import autodocument
from passlib.utils.handlers import BaseHandler
#local
__all__ = [
    'MySQL_323',
    'MySQL_41',
]

#=========================================================
#backend
#=========================================================
class MySQL_323(BaseHandler):
    #=========================================================
    #class attrs
    #=========================================================
    name = "mysql_323"
    setting_kwds = ()

    #=========================================================
    #formatting
    #=========================================================
    _pat = re.compile(r"^[0-9a-f]{16}$", re.I)

    @classmethod
    def identify(cls, hash):
        return bool(hash and cls._pat.match(hash))

    #=========================================================
    #backend
    #=========================================================
    #NOTE: using default genconfig

    @classmethod
    def genhash(cls, secret, config):
        if config and not cls.identify(config):
            raise ValueError, "not a mysql-41 hash"

        #FIXME: no idea if mysql has a policy about handling unicode passwords
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")

        MASK_32 = 0xffffffff
        MASK_31 = 0x7fffffff

        nr1 = 0x50305735
        nr2 = 0x12345671
        add = 7
        for c in secret:
            if c in ' \t':
                continue
            tmp = ord(c)
            nr1 ^= ((((nr1 & 63)+add)*tmp) + (nr1 << 8)) & MASK_32
            nr2 = (nr2+((nr2 << 8) ^ nr1)) & MASK_32
            add = (add+tmp) & MASK_32
        return "%08x%08x" % (nr1 & MASK_31, nr2 & MASK_31)

    #=========================================================
    #helpers
    #=========================================================
    #NOTE: using default encrypt() method

    @classmethod
    def verify(cls, secret, hash):
        if not hash:
            raise ValueError, "no hash specified"
        return hash.lower() == cls.genhash(secret, hash)

    #=========================================================
    #eoc
    #=========================================================

autodocument(MySQL_323)
register_crypt_handler(MySQL_323)

#=========================================================
#handler
#=========================================================
class MySQL_41(BaseHandler):
    #=========================================================
    #algorithm information
    #=========================================================
    name = "mysql_41"
    setting_kwds = ()

    #=========================================================
    #formatting
    #=========================================================
    _pat = re.compile(r"^\*[0-9A-F]{40}$", re.I)

    @classmethod
    def identify(cls, hash):
        return bool(hash and cls._pat.match(hash))

    #=========================================================
    #backend
    #=========================================================
    #NOTE: using default genconfig() method

    @classmethod
    def genhash(cls, secret, config):
        if config and not cls.identify(config):
            raise ValueError, "not a mysql-41 hash"
        #FIXME: no idea if mysql has a policy about handling unicode passwords
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")
        return '*' + sha1(sha1(secret).digest()).hexdigest().upper()

    #=========================================================
    #helpers
    #=========================================================
    #NOTE: using default encrypt() method

    @classmethod
    def verify(cls, secret, hash):
        if not hash:
            raise ValueError, "no hash specified"
        return hash.upper() == cls.genhash(secret, hash)

    #=========================================================
    #eoc
    #=========================================================

autodocument(MySQL_41)
register_crypt_handler(MySQL_41)
#=========================================================
#eof
#=========================================================
