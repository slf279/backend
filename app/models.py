from typing import Iterable
from datetime import date


class MikeRecord():
    class PrimaryKey(tuple):
        def __new__(self, mike_site_id: str, year: date):
            return super().__new__(self.__class__, (mike_site_id, year))

    def __init__(self, un_region: str, subregion_name: str, subregion_id: str,
                 country_name: str, country_code: str, mike_site_id: str,
                 mike_site_name: str, year: date,
                 total_number_of_carcasses: int,
                 number_of_illegal_carcasses: int) -> None:
        self.un_region = un_region
        self.subregion_name = subregion_name
        self.subregion_id = subregion_id
        self.country_name = country_name
        self.country_code = country_code
        self.mike_site_id = mike_site_id
        self.mike_site_name = mike_site_name
        self.year = year
        self.total_number_of_carcasses = total_number_of_carcasses
        self.number_of_illegal_carcasses = number_of_illegal_carcasses

    def get_primary_key(self) -> PrimaryKey:
        return self.PrimaryKey(self.mike_site_id, self.year)


### Abstract classes for Data Providers ###


class MasterPasswordProvider():
    def get_master_pwd(self) -> str:
        pass

    def set_master_pwd(self, new_pwd: str) -> str:
        pass


class MikeRecordProvider():
    def add_record(self, record: MikeRecord) -> bool:
        pass

    def add_records(self, records: Iterable[MikeRecord]):
        pass

    def get_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        pass

    def update_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        pass

    def remove_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        pass