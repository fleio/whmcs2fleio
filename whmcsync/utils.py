import logging
import bcrypt
import hmac
import hashlib
import re

LOG = logging.getLogger('whmcsync')


class PasswordTypes:
    """Supports all password types stored by WHMCS in time"""
    MD5 = 'm5'
    SALTED_MD5 = 'sm5'
    HMAC = 'hm'
    BCRYPT = 'bcr'
    UNKNOWN = 'unk'

    PATTERN_MD5 = re.compile('^[a-f0-9]{32}$')
    PATTERN_SALTED_MD5 = re.compile('^[a-f0-9]{32}(?::(.+))$')
    PATTERN_HMAC = re.compile('^[a-f0-9]{64}(?::(.+))$')
    PATTERN_BCRYPT = re.compile('^(\$2[axy]|\$2)\$[0-9]{0,2}\$[a-z0-9A-Z]{22}[a-zA-Z0-9/.]{31}$')

    choices = ((MD5, 'MD5'),
               (SALTED_MD5, 'SALTED MD5'),
               (HMAC, 'HMAC-SHA256'),
               (BCRYPT, 'Bcrypt'))

    @staticmethod
    def get_type(password):
        if PasswordTypes.PATTERN_BCRYPT.match(password):
            return PasswordTypes.BCRYPT
        elif PasswordTypes.PATTERN_HMAC.match(password):
            return PasswordTypes.HMAC
        elif PasswordTypes.PATTERN_SALTED_MD5.match(password):
            return PasswordTypes.SALTED_MD5
        elif PasswordTypes.PATTERN_MD5.match(password):
            return PasswordTypes.MD5
        else:
            return PasswordTypes.UNKNOWN

    @staticmethod
    def password_match(password, stored_password, hint=''):
        try:
            pass_type = PasswordTypes.get_type(stored_password)
        except Exception as e:
            LOG.exception(e)
            return None
        if pass_type == PasswordTypes.BCRYPT:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_password.password.encode('utf-8'))
            except Exception as e:
                LOG.exception(e)
                return None
        elif pass_type == PasswordTypes.HMAC:
            try:
                hmac_hash, secret = stored_password.split(':')
            except (TypeError, ValueError):
                LOG.error('Invalid WHMCS hmac password {}'.format(hint))
            else:
                digest = hmac.new(key=secret.encode('utf-8'),
                                  msg=password,
                                  digestmod=hashlib.sha256).hexdigest()
                return digest == hmac_hash
        elif pass_type == PasswordTypes.SALTED_MD5:
            try:
                md5hash_whmcs, salt = stored_password.split(':')
            except (TypeError, ValueError):
                LOG.error('Invalid MD5 salted password: {}'.format(hint))
                return None
            md5hash_password = hashlib.md5(''.join((salt, password)))
            return md5hash_whmcs == md5hash_password.hexdigest()
        elif pass_type == PasswordTypes.MD5:
            try:
                return hashlib.md5(password) == stored_password
            except (TypeError, ValueError):
                return None
