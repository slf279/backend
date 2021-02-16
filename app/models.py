from typing import Iterable
from datetime import date
from abc import ABC, abstractmethod


class MikeRecord():
    class PrimaryKey(tuple):
        def __new__(cls, mike_site_id: str, year: int):
            return super().__new__(cls.__class__, (mike_site_id, year))

    def __init__(self, un_region: str, subregion_name: str, subregion_id: str,
                 country_name: str, country_code: str, mike_site_id: str,
                 mike_site_name: str, year: int,
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


class MasterPasswordProvider(ABC):
    @abstractmethod
    def verify_pwd(self, plain_pwd: str) -> bool:
        pass

    @abstractmethod
    def set_master_pwd(self, new_pwd: str):
        pass


class MikeRecordProvider(ABC):
    @abstractmethod
    def add_record(self, record: MikeRecord):
        pass

    @abstractmethod
    def add_records(self, records: Iterable[MikeRecord]):
        pass

    @abstractmethod
    def get_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        pass

    @abstractmethod
    def get_all_records(self) -> Iterable[MikeRecord]:
        pass

    @abstractmethod
    def update_record(self, record_key: MikeRecord.PrimaryKey, updated_record: MikeRecord) -> MikeRecord:
        pass

    @abstractmethod
    def bulk_update_from_file(self, file_path: str):
        pass

    @abstractmethod
    def remove_record(self, record_key: MikeRecord.PrimaryKey) -> MikeRecord:
        pass
