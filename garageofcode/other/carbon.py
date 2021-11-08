import numpy as np

def main():
    fan_size = 1 # m^2
    wind_speed = 5 # m/s
    co2_concentration = 450e-6 # i.e. ppm
    air_density = 1.3e-3 # kg/m^3
    s_per_year = 3600 * 24 * 365 # s/y

    co2_per_year_per_m2 = fan_size * wind_speed * air_density * co2_concentration * s_per_year # kg / y

    print(co2_per_year_per_m2, "kg")

    person_co2_per_year = 1e4 # kg / y
    m2_per_person_per_year = person_co2_per_year / co2_per_year_per_m2

    print(m2_per_person_per_year, "m^2")



if __name__ == '__main__':
    main()