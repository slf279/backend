from typing import Iterable, Optional, Tuple
from datetime import date
from abc import ABC, abstractmethod


class MikeRecord:
    class PrimaryKey(tuple):
        def __new__(cls, mike_site_id: str, year: int):
            return super().__new__(cls.__class__, (mike_site_id, year))

    def __init__(self, un_region: str, subregion_name: str, subregion_id: str,
                 country_name: str, country_code: str, mike_site_id: str,
                 mike_site_name: str, year: int,
                 carcasses: int, illegal_carcasses: int) -> None:
        self.un_region = un_region
        self.subregion_name = subregion_name
        self.subregion_id = subregion_id
        self.country_name = country_name
        self.country_code = country_code
        self.mike_site_id = mike_site_id
        self.mike_site_name = mike_site_name
        self.year = year
        self.carcasses = carcasses
        self.illegal_carcasses = illegal_carcasses

    def get_primary_key(self) -> PrimaryKey:
        return self.PrimaryKey(self.mike_site_id, self.year)

    def to_tuple(self) -> Tuple[str, str, str, str, str, str, str, int, int, int]:
        """
        Returns this object as a tuple

        :return: (un_region, subregion_name, subregion_id, country_name, country_code, mike_site_id, mike_site_name,
             mike_year, carcasses, illegal_carcasses)
        """
        return (self.un_region,
                self.subregion_name,
                self.subregion_id,
                self.country_name,
                self.country_code,
                self.mike_site_id,
                self.mike_site_name,
                self.year,
                self.carcasses,
                self.illegal_carcasses)

    @classmethod
    def from_tuple(cls, tuple_record: Tuple[str, str, str, str, str, str, str, int, int, int]):
        """
        Constructs a MikeRecord from a tuple

        :param tuple_record: (un_region, subregion_name, subregion_id, country_name, country_code, mike_site_id,
            mike_site_name, year, carcasses, illegal_carcasses)
        :return: MikeRecord
        """
        return cls(tuple_record[0], tuple_record[1], tuple_record[2], tuple_record[3], tuple_record[4], tuple_record[5],
                   tuple_record[6], tuple_record[7], tuple_record[8], tuple_record[9])


class CountryRecord:
    class PrimaryKey(tuple):
        def __new__(cls, country_code: str, year: int):
            return super().__new__(cls.__class__, (country_code, year))

    def __init__(self, country_name: str, country_code: str, year: int, carcasses: int,
                 illegal_carcasses: int) -> None:
        self.country_name = country_name
        self.country_code = country_code
        self.year = year
        self.carcasses = carcasses
        self.illegal_carcasses = illegal_carcasses

    def get_primary_key(self) -> PrimaryKey:
        return self.PrimaryKey(self.country_code, self.year)

    @classmethod
    def from_tuple(cls, tuple_record: Tuple[str, str, int, int, int]):
        """
        Constructs a CountryRecord from a tuple

        :param tuple_record: (country_name, country_code, year, carcasses, illegal_carcasses)
        :return: CountryRecord
        """
        return cls(tuple_record[0], tuple_record[1], tuple_record[2], tuple_record[3], tuple_record[4])


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
    def add_mike_record(self, record: MikeRecord):
        pass

    @abstractmethod
    def add_mike_records(self, records: Iterable[MikeRecord]):
        pass

    @abstractmethod
    def get_mike_record(self, record_key: MikeRecord.PrimaryKey) -> Optional[MikeRecord]:
        pass

    @abstractmethod
    def get_all_mike_records(self) -> Iterable[MikeRecord]:
        pass

    @abstractmethod
    def update_mike_record(self, record_key: MikeRecord.PrimaryKey, updated_record: MikeRecord) -> Optional[MikeRecord]:
        pass

    @abstractmethod
    def bulk_update_mike_records(self, records: Iterable[MikeRecord]):
        pass

    @abstractmethod
    def remove_mike_record(self, record_key: MikeRecord.PrimaryKey):
        pass


class CountryRecordProvider(ABC):
    @abstractmethod
    def get_country_record(self, record_key: CountryRecord.PrimaryKey) -> Optional[CountryRecord]:
        pass

    @abstractmethod
    def get_all_country_records(self) -> Iterable[CountryRecord]:
        pass
