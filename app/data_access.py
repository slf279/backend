import mariadb
from os import path
from flask import Flask
from .models import MikeRecord, MikeRecordProvider, MasterPasswordProvider
from typing import Iterable
from passlib.hash import argon2


class MariaDBRecordProvider(MikeRecordProvider):
    def __init__(self, config: dict) -> None:
        self.pool = mariadb.connect(host=config['DB_HOST'],
                                    port=config['DB_PORT'],
                                    user=config['DB_USER'],
                                    password=config['DB_PASSWORD'],
                                    pool_name="capstone-backend",
                                    pool_size=20)

    # TODO: Implement all of MikeRecordProvider's methods

    def add_record(self, record: MikeRecord) -> bool:
        with self.pool.get_connection() as conn:
            pass

    def add_records(self, records: Iterable[MikeRecord]):
        with self.pool.get_connection() as conn:
            pass

    def get_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        with self.pool.get_connection() as conn:
            pass

    def update_record(self, record_key: MikeRecord.PrimaryKey):
        with self.pool.get_connection() as conn:
            pass

    def remove_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        with self.pool.get_connection() as conn:
            pass


class NoMasterPasswordException(Exception):
    pass


class TextFileMasterPasswordProvider(MasterPasswordProvider):
    def __init__(self, instance_folder: str) -> None:
        self.master_pwd_file = path.join(instance_folder, 'password.txt')

    def get_master_pwd(self) -> str:
        if path.isfile(self.master_pwd_file):
            with open(self.master_pwd_file, 'r') as f:
                master_pwd = f.read()
                if master_pwd == '':
                    raise NoMasterPasswordException()
                else:
                    return master_pwd
        else:
            raise NoMasterPasswordException()

    def set_master_pwd(self, new_pwd: str):
        with open(self.master_pwd_file, 'w') as f:
            f.write(argon2.hash(new_pwd))