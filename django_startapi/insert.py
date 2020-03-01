import os


class Insert:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r+') as f:
                self._data = f.readlines()
        else:
            self._data = []
        return self

    def __exit__(self, type, value, traceback):
        with open(self.filename, 'w') as f:
            f.writelines(self._data)

    def search_index(self, value, last=False):
        line_num = 0
        found = False
        for num, line in enumerate(self._data):
            if type(value) == str:
                startswith = line.startswith(value)
            elif type(value) == list:
                startswith = any(line.startswith(v) for v in value)
            else:
                raise TypeError(value)
            if startswith:
                line_num = num
                found = True
                if not last:
                    break
        if not found:
            raise Exception('Line startswith %s not found in %s'
                            % (value, self.filename))
        return line_num

    def at_value(self, value, content):
        index = self.search_index(value)
        self._data.insert(index, content)

    def at_index(self, index, content):
        self._data.insert(index, content)

    def before(self, value, content):
        index = self.search_index(value)
        if index > 0:
            index -= 1
        self._data.insert(index, content)

    def after(self, value, content, last=False):
        index = self.search_index(value, last)
        if index < len(self._data):
            index += 1
        self._data.insert(index, content)

    def append(self, content):
        if type(content) == str:
            self._data.append(content)
        elif type(content) == list:
            self._data.extend(content)
        else:
            raise TypeError(content)
