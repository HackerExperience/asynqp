from io import BytesIO
import contexts
from asynqp import serialisation, AMQPError


class WhenParsingATable:
    @classmethod
    def examples_of_tables(self):
        yield b"\x00\x00\x00\x0E\x04key1t\x00\x04key2t\x01", {'key1': False, 'key2': True}
        yield b"\x00\x00\x00\x0B\x03keys\x05hello", {'key': 'hello'}
        yield b"\x00\x00\x00\x0E\x03keyS\x00\x00\x00\x05hello", {'key': 'hello'}
        yield b"\x00\x00\x00\x16\x03keyF\x00\x00\x00\x0D\x0Aanotherkeyt\x00", {'key': {'anotherkey': False}}

    def because_we_read_the_table(self, bytes, expected):
        self.result = serialisation.read_table(BytesIO(bytes))

    def it_should_return_the_table(self, bytes, expected):
        assert self.result == expected


class WhenParsingABadTable:
    @classmethod
    def examples_of_bad_tables(self):
        yield b"\x00\x00\x00\x0F\x04key1t\x00\x04key2t\x01"  # length too long
        yield b"\x00\x00\x00\x06\x04key1X"  # bad value type code

    def because_we_read_the_table(self, bytes):
        self.exception = contexts.catch(serialisation.read_table, BytesIO(bytes))

    def it_should_throw_an_AMQPError(self):
        assert isinstance(self.exception, AMQPError)


class WhenParsingALongString:
    def because_we_read_a_long_string(self):
        self.result = serialisation.read_long_string(BytesIO(b"\x00\x00\x00\x05hello"))

    def it_should_return_the_string(self):
        assert self.result == 'hello'


class WhenParsingABadLongString:
    def because_we_read_a_bad_long_string(self):
        self.exception = contexts.catch(serialisation.read_long_string, BytesIO(b"\x00\x00\x00\x10hello"))  # length too long

    def it_should_throw_an_AMQPError(self):
        assert isinstance(self.exception, AMQPError)


class WhenPackingBools:
    @classmethod
    def examples_of_bools(self):
        yield [False], b"\x00"
        yield [True], b"\x01"
        yield [True, False, True], b'\x05'
        yield [True, False], b'\x01'
        yield [True, True, True, True, True, True, True, True], b'\xFF'

    def because_I_pack_them(self, bools, expected):
        self.result = serialisation.pack_bools(*bools)

    def it_should_pack_them_correctly(self, bools, expected):
        assert self.result == expected
