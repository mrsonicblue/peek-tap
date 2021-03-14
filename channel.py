class Channel:
    EOM = 4
    ENCODING = 'utf-8'

    def __init__(self, serial):
        self.serial = serial
        self.read_buffer = bytearray()
        self.read_position = 0
        self.command_stack = []

    def read(self):
        result = []

        in_waiting = self.serial.in_waiting
        if in_waiting > 0:
            packet = self.serial.read(in_waiting)
            read_length = len(packet)

            self.read_buffer.extend(packet)

            for i in range(read_length):
                if self.read_buffer[0] == Channel.EOM: # End of stack
                    result.append(self.command_stack)
                    self.command_stack = []

                    self.read_buffer[:1] = b''
                elif self.read_buffer[self.read_position] == 0:
                    command = self.read_buffer[:self.read_position].decode(Channel.ENCODING)
                    self.command_stack.append(command)

                    self.read_buffer[:(self.read_position + 1)] = b''

                    self.read_position = 0
                else:
                    self.read_position += 1
                
        return result
    
    def write(self, command_stack):
        packet = bytearray()
        for command in command_stack:
            packet.extend(command.encode(Channel.ENCODING))
            packet.append(0)
        packet.append(Channel.EOM)

        self.serial.write(packet)