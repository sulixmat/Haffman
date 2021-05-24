import binascii


class Hemming:
    def __init__(self, in_message: str, unit_length: int):
        assert not unit_length % 8, 'unit length must be multiples 8'
        self.encode_unit_length = unit_length
        self.message: str = in_message
        self.message_bin_array = self.chars_to_bin(in_message)
        self.control_bits_pos = [i - 1 for i in range(1, self.encode_unit_length + 1) if not i & (i - 1)]
        self.decode_unit_length = self.encode_unit_length + len(self.control_bits_pos)

    @staticmethod
    def chars_to_bin(input_message):
        return ''.join([bin(ord(c))[2:].zfill(8) for c in input_message])

    @staticmethod
    def unit_iterator(binary_message, unit_length):
        """
        Берем строку из набора битов и разделяем по заданной длине юнита
        Может работать с закодированным и раскодированным сообщениями (в конструкторе класса есть занчения)
        """
        for i in range(len(binary_message)):
            if not i % unit_length:
                yield binary_message[i:i + unit_length]

    @property
    def encode_message(self):
        encoded_message = str()
        for item in self.unit_iterator(self.message_bin_array, self.encode_unit_length):
            encoded_message += self.set_control_bits(item, self.control_bits_pos)
        return encoded_message

    @property
    def decode_message(self):
        encoded_message = self.encode_message
        decoded_message = str()
        for i, unit in enumerate(self.unit_iterator(encoded_message, self.decode_unit_length)):
            unit_control_bits: dict = self.__get_control_bits(unit)
            decoded_unit = ''.join([item for i, item in enumerate(unit) if i not in unit_control_bits])
            #####################################
            if i == 3:
                decoded_unit = list(decoded_unit)
                if decoded_unit[2] == 1:
                    decoded_unit[2] = '0'
                    decoded_unit = ''.join(decoded_unit)
                else:
                    decoded_unit[2] = '1'
                    decoded_unit = ''.join(decoded_unit)
            #####################################
            if self.__find_error(decoded_unit, unit_control_bits):
                # сори за лапшу
                encode_decoded_unit_control_bits = self.__get_control_bits(self.set_control_bits(decoded_unit, self.control_bits_pos))
                decoded_message = self.fix_error(unit_control_bits, encode_decoded_unit_control_bits)
            else:
                pass
            decoded_message += decoded_unit

        return decoded_message

    @staticmethod
    def __get_control_bit(message_unit_part):
        return '0' if (message_unit_part.count('1') % 2) == 0 else '1'

    @staticmethod
    def __get_control_bits(encoded_message_unit):
        control_bits = dict()
        for i, item in enumerate(encoded_message_unit):
            if not (i+1) & i:
                control_bits[int(i)] = item
        return control_bits

    def __find_error(self, decoded_unit, check_bits):
        encode_decoded_unit = self.set_control_bits(decoded_unit, self.control_bits_pos)
        encode_decoded_unit_control_bits = self.__get_control_bits(encode_decoded_unit)

        return True if (check_bits != encode_decoded_unit_control_bits) else False

    @staticmethod
    def set_control_bits(message_unit, control_bits_pos):
        temp_var = message_unit
        for value in range(len(message_unit)):
            if value in control_bits_pos:
                control_bit = Hemming.__get_control_bit(message_unit[value:])
                temp_var = temp_var[:value] + control_bit + temp_var[value:]
        return temp_var

    @staticmethod
    def fix_error(unit_control_bits, encode_decoded_unit_control_bits):
        encoded_unit = str()
        if encode_decoded_unit_control_bits != unit_control_bits:
            invalid_bits = []
            for encode_decoded_unit_control_bits, value in encode_decoded_unit_control_bits.items():
                if unit_control_bits[encode_decoded_unit_control_bits] != value:
                    invalid_bits.append(encode_decoded_unit_control_bits)
            num_bit = sum(invalid_bits)
            encoded_unit = '{0}{1}{2}'.format(
                unit_control_bits[:num_bit - 1],
                int(unit_control_bits[num_bit - 1]) ^ 1,
                unit_control_bits[num_bit:])
        return encoded_unit


if __name__ == '__main__':
    x = Hemming('Pep', 8)
    print(f'Начальный набор бит: {x.message_bin_array}')
    print(f'Закодированное сообщение: {x.encode_message}')
    print(f'Раскодированное сообщение: {x.decode_message}')
    print(f'Равенство исходного и раскодированного сообщения: {(x.message_bin_array == x.decode_message)}')
    message = int(x.decode_message, 2)
    message = binascii.unhexlify('%x' % message)
    print(f'Сообщение: {message}')
