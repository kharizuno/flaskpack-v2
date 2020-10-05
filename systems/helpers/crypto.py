# -*- coding: utf-8 -*-
import hashlib
import bcrypt


def md5_text(text) -> str:
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()


def bcrypt_password(plain_password) -> str:
    """convert string to bcrypt'd string"""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt(prefix=b"2a")).decode('utf-8')


def encryt_passhash(plain_password) -> str:
    """convert string to bcrypt'd string

    an alias to `bcrypt_password`
    """
    return bcrypt_password(plain_password)


def compare_passhash(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf8'), hashed.encode('utf8'))
