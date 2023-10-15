class CommandStorage:
    def __init__(self):
        self._commands = []
        self._keys = ['id', 'command_name', 'command', 'output', 'status', 'time_of_execution', 'duration']
        
    def add_command(self, command_dict):
        try : 
            assert set(command_dict.keys()) == set(self._keys)
            self._commands.append(command_dict)
        except AssertionError :
            print("Incompatible command format. Operation failed.")

    def remove_command(self, index=-1):
        try : 
            assert self.num_commands != 0
            if index < 0:
                index = len(self._commands) + index
            if 0 <= index < len(self._commands):
                return self._commands.pop(index)
            else :
                raise IndexError("Index out of range")
        except AssertionError :
            print("No commands found. Operation failed.")
        

    def sort_commands_by_date(self):
        self._commands.sort(key=lambda x: x["date_added"])

    @property
    def num_commands(self):
        return len(self._commands)

    def get_commands(self):
        return self._commands