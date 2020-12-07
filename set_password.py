from app.data_access import TextFileMasterPasswordProvider
from sys import argv, stderr, exit
from os import path
from passlib.hash import argon2


def main():
    if len(argv) == 2 and argv[1] != '':
        pass
    else:
        print('This program requires a new password.', file=stderr)
        exit(1)
    pwd_store = TextFileMasterPasswordProvider(
        path.join(path.curdir, 'instance'))
    pwd_store.set_master_pwd(argon2.hash(argv[1]))
    print('The master password has been reset.')
    exit(0)


if __name__ == "__main__":
    main()