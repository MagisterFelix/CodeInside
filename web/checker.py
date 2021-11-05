import subprocess
from time import perf_counter
from memory_profiler import memory_usage


class Checker:

    def __init__(self, user, task, language, code):
        self.user = user
        self.task = task
        self.language = language
        self._code = code
        self._message = 'Incomplete'
        self._status = None
        self._time = 'N/A'
        self._memory = 'N/A'
        self._max_time = self.task.complexity * 1000
        self._max_memory = 64
        self._ext = {
            'Python': '.py',
            'C++': '.cpp',
            'C#': '.cs',
            'Java': '.java',
            'JavaScript': '.js'
        }
        self._output = None
        self._error = None

    def run(self, command, test=''):
        start_time = perf_counter()
        proc = subprocess.Popen(command,
                                stdin=open(f'input_{self.user.id}.txt', 'r'),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                shell=True)
        memory = sum(memory_usage(proc=proc, timeout=5.0))
        self._output, self._error = (b_string.strip() for b_string in proc.communicate(input=test, timeout=5.0))
        proc.kill()
        finish_time = (perf_counter() - start_time) * 1000
        return (float(f'{(finish_time):.2f}'), float(f'{memory:.2f}'))

    def check(self):
        input = self.task.input.split('\r\n\r\n')
        with open(f'input_{self.user.id}.txt', 'w') as file:
            file.write(input[0])

        expected_output = self.task.output.split('\r\n\r\n')

        time = 0
        memory = 0
        output = []

        if self.language == 'Java':
            self._code = self._code.replace('public class Main', f'class test_{self.user.id}')

        file_name = f'test_{self.user.id}' + self._ext[self.language]

        with open(file_name, 'w') as file:
            file.write(self._code)

        try:
            if self.language == 'Python':
                cmd = f'python {file_name}'
                self.run(cmd, input[0])

            if self.language == 'C++':
                cmd = f'./test_{self.user.id}.out'
                self.run(f'g++ {file_name} -o {cmd[2:]}')
                subprocess.run(f'rm {file_name}', shell=True)
                file_name = f'test_{self.user.id}.out'

            if self.language == 'C#':
                cmd = f'mono test_{self.user.id}.out'
                self.run(f'mcs -out:{file_name[:-3]}.out {file_name}')
                subprocess.run(f'rm {file_name}', shell=True)
                file_name = f'test_{self.user.id}.out'

            if self.language == 'Java':
                cmd = f'java {file_name[:-5]}'
                self.run(f'javac {file_name}')
                subprocess.run(f'rm {file_name}', shell=True)
                file_name = f'{file_name[:-5]}.class'

            if self.language == 'JavaScript':
                cmd = f'node {file_name}'
                self.run(cmd, input[0])

            if len(self._error) and self._error.find('JAVA_TOOL_OPTIONS') == -1:
                self._status = 'System failure'
                self._message = self._error
                subprocess.run(f'rm {file_name}', shell=True)
                return

            for test in input:
                with open(f'input_{self.user.id}.txt', 'w') as file:
                    file.write(test)

                current_time, current_memory = self.run(cmd, test)

                self._time = f'{current_time} ms'
                self._memory = f'{current_memory} MB'

                if current_time > self._max_time:
                    self._status = 'Time limit exceeded'
                    self._time = 'N/A'
                    self._memory = 'N/A'
                    break

                if current_memory > self._max_memory:
                    self._status = 'Memory limit exceeded'
                    self._time = 'N/A'
                    self._memory = 'N/A'
                    break

                output.append(self._output)
                time = max(time, current_time)
                memory = max(memory, current_memory)
            else:
                self._message = 'Complete'
                self._status = 'Accepted' if output == expected_output else 'Wrong answer'
                self._time = f'{time} ms'
                self._memory = f'{memory} MB'
        except subprocess.TimeoutExpired:
            self._status = 'Time limit exceeded'
            self._time = 'N/A'
            self._memory = 'N/A'

        subprocess.run(f'rm {file_name} input_{self.user.id}.txt', shell=True)

    def get_data(self):
        data = {
            'status': self._status,
            'time': self._time,
            'memory': self._memory
        }
        return data

    @property
    def message(self):
        return self._message
