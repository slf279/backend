import mariadb
from os import path
from .models import MikeRecord, CountryRecord, MikeRecordProvider, CountryRecordProvider, MasterPasswordProvider
from typing import Iterable
from argon2 import PasswordHasher


class MariaDBRecordProvider(MikeRecordProvider, CountryRecordProvider):

    def __init__(self, config: dict) -> None:
        self.pool = mariadb.connect(host=config['DB_HOST'],
                                    port=config['DB_PORT'],
                                    user=config['DB_USER'],
                                    password=config['DB_PASSWORD'],
                                    pool_name="all-ears",
                                    pool_size=20)

    # Implements MikeRecordProvider

    def add_mike_record(self, record: MikeRecord):
        with self.pool.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "insert into elephantcarcasses "
                "( un_region"
                ", subregion_name"
                ", subregion_id"
                ", country_name"
                ", country_code"
                ", mike_site_id"
                ", mike_site_name"
                ", mike_year"
                ", carcasses"
                ", illegal_carcasses ) "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", record.to_tuple())

    def add_mike_records(self, records: Iterable[MikeRecord]):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "insert into elephantcarcasses "
                    "( un_region"
                    ", subregion_name"
                    ", subregion_id"
                    ", country_name"
                    ", country_code"
                    ", mike_site_id"
                    ", mike_site_name"
                    ", mike_year"
                    ", carcasses"
                    ", illegal_carcasses ) "
                    "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list(map(lambda x: x.to_tuple(), records)))

    def get_mike_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select "
                            "un_region"
                            ", subregion_name"
                            ", subregion_id"
                            ", country_name"
                            ", country_code"
                            ", mike_site_id"
                            ", mike_site_name"
                            ", mike_year"
                            ", carcasses"
                            ", illegal_carcasses "
                            "from elephantcarcasses "
                            "where mike_site_id = ? and mike_year = ?", record_key)
                return MikeRecord.from_tuple(cur.fetchone())

    def get_all_mike_records(self) -> Iterable[MikeRecord]:
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select * from elephantcarcasses")
                return list(map(lambda x: MikeRecord.from_tuple(x), cur.fetchall()))

    def update_mike_record(self, record_key: MikeRecord.PrimaryKey, updated_record: MikeRecord):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                if record_key == updated_record.get_primary_key():
                    cur.execute("update elephantcarcasses set "
                                "un_region = ?"
                                ", subregion_name = ?"
                                ", subregion_id = ?"
                                ", country_name = ?"
                                ", country_code = ?"
                                ", mike_site_id = ?"
                                ", mike_site_name = ?"
                                ", mike_year = ?"
                                ", carcasses = ?"
                                ", illegal_carcasses = ? "
                                "where mike_site_id = ? and mike_year = ?", updated_record.to_tuple() + record_key)

    def bulk_update_mike_records(self, records: Iterable[MikeRecord]):
        pass

    def remove_mike_record(self, record_key: MikeRecord.PrimaryKey):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("delete from elephantcarcasses where mike_site_id = ? and mike_year = ?",
                            record_key)

    # Implements CountryRecordProvider

    def get_country_record(self, record_key: CountryRecord.PrimaryKey) -> CountryRecord:
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select "
                    "country_name"
                    ", country_code"
                    ", mike_year"
                    ", sum(carcasses) as carcasses"
                    ", sum(illegal_carcasses) as illegal_carcasses "
                    "from elephantcarcasses "
                    "where country_code = ? and mike_year = ? "
                    "group by country_code, mike_year", record_key)
                return CountryRecord.from_tuple(cur.fetchone())

    def get_all_country_records(self) -> Iterable[CountryRecord]:
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select "
                    "country_name"
                    ", country_code"
                    ", mike_year"
                    ", sum(carcasses) as carcasses"
                    ", sum(illegal_carcasses) as illegal_carcasses "
                    "from elephantcarcasses "
                    "group by country_code, mike_year")
                return list(map(lambda x: CountryRecord.from_tuple(x), cur.fetchall()))


class NoMasterPasswordException(Exception):
    pass


class TextFileMasterPasswordProvider(MasterPasswordProvider):
    def __init__(self, instance_folder: str) -> None:
        self.master_pwd_file = path.join(instance_folder, 'password.txt')

    def verify_pwd(self, plain_pwd: str) -> bool:
        if path.isfile(self.master_pwd_file):
            with open(self.master_pwd_file, 'r') as f:
                master_pwd_hash = f.read()
                if master_pwd_hash == '':
                    raise NoMasterPasswordException()
                else:
                    return PasswordHasher().verify(master_pwd_hash, plain_pwd)
        else:
            raise NoMasterPasswordException()

    def set_master_pwd(self, new_pwd: str):
        with open(self.master_pwd_file, 'w') as f:
            f.write(PasswordHasher().hash(new_pwd))
