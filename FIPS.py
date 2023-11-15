class Fips:
    def __init__(self, fips_code, county_name, postal_state, code):
        self.fips_code = fips_code
        self.county_name = county_name
        self.postal_state = postal_state
        self.code = code

    def __str__(self):
        return f"{self.fips_code} || {self.county_name} || {self.postal_state} || {self.code}"