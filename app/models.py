from typing import Tuple


class MikeRecord(object):
    def __init__(self, id: int, un_region: str, subregion_name: str,
                 subregion_id: str, country_name: str, country_code: str,
                 mike_site_id: str, mike_site_name: str, year: int,
                 total_number_of_carcasses: int,
                 number_of_illegal_carcasses: int) -> None:
        self.id = id
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

    def get_primary_key(self) -> Tuple[str, int]:
        return (self.mike_site_id, self.year)
