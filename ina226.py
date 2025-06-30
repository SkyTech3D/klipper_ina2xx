import logging
from . import bus

INA226_I2C_ADDR = 0x40  # Default INA226 address (can be changed)
SHUNT_RESISTOR_OHMS = 0.1  # Shunt resistor value in ohms

INA226_REG_CONFIG = 0x00
INA226_REG_SHUNT_VOLTAGE = 0x01
INA226_REG_BUS_VOLTAGE = 0x02
INA226_REG_POWER = 0x03
INA226_REG_CURRENT = 0x04
INA226_REG_CALIBRATION = 0x05

class INA226:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = None
        self.name = config.get_name().split()[-1]
        self.report_time = config.getint("report_time", 30, minval=5)

        self.i2c = bus.MCU_I2C_from_config(
            config, default_addr=INA226_I2C_ADDR, default_speed=100000
        )

        self._callback = None

        self.shunt_voltage = 0
        self.bus_voltage = 0
        self.current = 0
        self.power = 0

        self.calibration_value = 0
        self.current_lsb = config.getfloat('current_lsb', 0.001,above=0.)  # default 1mA per bit, adjust as needed
        self.power_lsb = self.current_lsb * 25    # power LSB (25x current LSB)

        self.reactor = self.printer.get_reactor()
        self.sample_timer = None

        self.printer.register_event_handler("klippy:connect", self._handle_connect)
        self.printer.add_object("ina226 " + self.name, self)

    def _handle_connect(self):
        self._init_ina226()
        if self.sample_timer is None:
            self.sample_timer = self.reactor.register_timer(self._sample_ina226)
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def _init_ina226(self):
        # Configure INA226 (Example config: avg=4, bus conv time=1100us, shunt conv time=1100us, mode=continuous)
        config = (
            (0b010 << 9) |  # Averaging mode = 4 samples
            (0b100 << 6) |  # Bus voltage conversion time = 1.1ms
            (0b100 << 3) |  # Shunt voltage conversion time = 1.1ms
            0b111           # Mode = Shunt and bus continuous
        )
        self._write_register(INA226_REG_CONFIG, config)
        self._write_register(INA226_REG_CALIBRATION, self.calibration_value)

    def _write_register(self, reg, value):
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.i2c.i2c_write([reg] + data)

    def _read_register(self, reg):
        response = self.i2c.i2c_read([reg], 2)["response"]
        msb, lsb = response
        return (msb << 8) | lsb

    def _to_signed_int16(self, value):
        if value & 0x8000:
            return value - 0x10000
        return value

    def _sample_ina226(self, eventtime):
        try:
            self.read()
        except Exception as e:
            logging.error(f"ina226: Error reading data: {str(e)}")
            self.shunt_voltage = self.bus_voltage = self.current = self.power = 0

        measured_time = self.reactor.monotonic()
        print_time = self.i2c.get_mcu().estimated_print_time(measured_time)
        if self._callback:
            self._callback(print_time, self.get_status(eventtime))

        return measured_time + self.report_time

    def read(self):
        # Read shunt voltage (signed 16 bit, LSB = 2.5uV)
        raw_shunt = self._to_signed_int16(self._read_register(INA226_REG_SHUNT_VOLTAGE))
        self.shunt_voltage = raw_shunt * 0.0000025  # 2.5uV per bit

        # Read bus voltage (unsigned 16 bit, LSB = 1.25mV)
        raw_bus = self._read_register(INA226_REG_BUS_VOLTAGE)
        self.bus_voltage = raw_bus * 0.00125  # 1.25mV per bit

        # Read current (signed 16 bit)
        raw_current = self._to_signed_int16(self._read_register(INA226_REG_CURRENT))
        self.current = raw_current * self.current_lsb

        # Read power (unsigned 16 bit)
        raw_power = self._read_register(INA226_REG_POWER)
        self.power = raw_power * self.power_lsb

        logging.info(
            f"ina226: shunt_voltage={self.shunt_voltage:.6f}V, "
            f"bus_voltage={self.bus_voltage:.3f}V, "
            f"current={self.current:.6f}A, "
            f"power={self.power:.6f}W"
        )
        return True

    def setup_callback(self, cb):
        self._callback = cb

    def get_shunt_voltage(self):
        return self.shunt_voltage

    def get_bus_voltage(self):
        return self.bus_voltage

    def get_current(self):
        return self.current

    def get_power(self):
        return self.power

    def get_status(self, eventtime):
        return {
            "shunt_voltage": self.get_shunt_voltage(),
            "bus_voltage": self.get_bus_voltage(),
            "current": self.get_current(),
            "power": self.get_power(),
        }

def load_config(config):
    """Load the INA226 module."""
    return INA226(config)

def load_config_prefix(config):
    """Load the INA226 module with a prefix."""
    return INA226(config)