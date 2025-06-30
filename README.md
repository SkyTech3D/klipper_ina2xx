# klipper_ina2xx

This repository provides a Klipper extension for interfacing with the Texas Instruments INA226 current/voltage/power monitor over I2C. It enables real-time monitoring of shunt voltage, bus voltage, current, and power, which is useful for 3D printer power diagnostics and monitoring.

## Features

- Reads shunt voltage, bus voltage, current, and power from the INA226 sensor.
- Configurable reporting interval and current LSB.
- Integrates with Klipper's event and timer system.
- Optional Moonraker update manager integration.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/SkyTech3D/klipper_ina2xx.git
   cd klipper_ina2xx
   ```

2. **Run the install script:**
    ```sh
    ./install.sh
    ```

This will symlink `ina226.py` into your Klipper extras directory. The script can also add an `[update_manager]` block to your `moonraker.conf` for easy updates.

3. **Configure Klipper:**
 Add the following section to your Klipper configuration file (e.g., `printer.cfg`):

    ```
    [ina226 my_sensor]
    i2c_bus: <your_i2c_bus>
    current_lsb: 0.001  # Optional, default is 0.001 (1mA per bit)
    report_time: 30     # Optional, reporting interval in seconds
    ```

Replace `<your_i2c_bus>` with the appropriate I2C bus for your setup.

4. **Restart Klipper and Moonraker:**
    ```sh
    sudo service klipper restart
    sudo service moonraker restart
    ```

## Wiring the INA226 Sensor

The INA226 sensor is connected to your MCU via I2C and measures current using a shunt resistor. Below is a simplified wiring diagram:

```
MCU (e.g. Raspberry Pi, MCU board)
   |      |      |      |
  SDA   SCL    GND    VCC (3.3V or 5V)
   |      |      |      |
   |______|______|______|
          |
      INA226 Module
        ^     |
        |     v
       PSU  LOAD (e.g. heater, fan, etc.)
```

**Wiring steps:**
- Connect the INA226 `SDA` and `SCL` pins to the corresponding I2C pins on your MCU.
- Connect `VCC` and `GND` to power and ground.
- Place the INA226 (`VIN+`, `VIN-`)  in series with the load you want to measure.

For more details, refer to the [INA226 datasheet (Texas Instruments)](https://www.ti.com/lit/ds/symlink/ina226.pdf).

## Usage

After installation and configuration, the INA226 sensor readings will be available in Klipper and can be accessed via macros, Moonraker API, or custom scripts.

## License

MIT License