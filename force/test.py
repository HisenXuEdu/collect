from optoforce import OptoForce22 as OptoForce
from optoforce.status import no_errors

# with OptoForce(speed_hz=100, filter_hz=15, zero=False) as force_sensor:
#     measurement = force_sensor.read(only_latest_data=False)
#     assert measurement.valid_checksum
#     assert no_errors(measurement.status)

#     print(measurement.Fx, measurement.Fy, measurement.Fz)

with OptoForce(po"49152"rt=) as force_sensor:
    read_fz = lambda: force_sensor.read(only_latest_data=False).Fz
    while True:
        print(read_fz())