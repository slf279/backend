import mariadb
from os import path
from .models import MikeRecord, CountryRecord, MikeRecordProvider, CountryRecordProvider, MasterPasswordProvider
from typing import Iterable, Optional
from argon2 import PasswordHasher


class RecordAlreadyExistsException(Exception):
    pass


class MariaDBRecordProvider(MikeRecordProvider, CountryRecordProvider):

    def __init__(self, config: dict) -> None:
        self.pool = mariadb.connect(host=config['DB_HOST'],
                                    port=config['DB_PORT'],
                                    user=config['DB_USER'],
                                    password=config['DB_PASSWORD'],
                                    database=config['DB_NAME'],
                                    pool_name="all-ears",
                                    pool_size=20)

    # Implements MikeRecordProvider

    def add_mike_record(self, record: MikeRecord):
        with self.pool.get_connection() as conn:
            cur = conn.cursor()
            try:
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
            except mariadb.IntegrityError:
                raise RecordAlreadyExistsException()

    def add_mike_records(self, records: Iterable[MikeRecord]):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                try:
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
                except mariadb.IntegrityError:
                    raise RecordAlreadyExistsException()

    def get_mike_record(self, record_key: MikeRecord.PrimaryKey) -> Optional[MikeRecord]:
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
            if cur.fieldcount() == 0:
                return None
            else:
                return MikeRecord.from_tuple(cur.fetchone())

    def get_all_mike_records(self) -> Iterable[MikeRecord]:
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select * from elephantcarcasses")
                if cur.fieldcount() == 0:
                    return []
                else:
                    return map(lambda x: MikeRecord.from_tuple(x), cur)

    def update_mike_record(self, record_key: MikeRecord.PrimaryKey, updated_record: MikeRecord):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
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
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany("replace into elephantcarcasses "
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
                                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list(records))

    def remove_mike_record(self, record_key: MikeRecord.PrimaryKey):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("delete from elephantcarcasses "
                            "where mike_site_id = ? and mike_year = ?",
                            record_key)

    # Implements CountryRecordProvider

    def get_country_record(self, record_key: CountryRecord.PrimaryKey) -> Optional[CountryRecord]:
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
                if cur.fieldcount() == 0:
                    return None
                else:
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
                if cur.fieldcount() == 0:
                    return []
                else:
                    return map(lambda x: CountryRecord.from_tuple(x), cur)


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
