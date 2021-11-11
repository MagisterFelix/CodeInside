import os
import subprocess
from threading import Timer
from concurrent.futures import ThreadPoolExecutor
from functools import wraps


def threadpool(f, executor=None):

    @wraps(f)
    def wrap(*args, **kwargs):
        return (executor or ThreadPoolExecutor()).submit(f, *args, **kwargs).result()

    return wrap


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
        self._max_memory = 128
        self._output = None
        self._error = None

    @threadpool
    def run(self, command, test=subprocess.DEVNULL):
        proc = subprocess.Popen(command,
                                stdin=open(f'input_{self.user.id}.txt', 'r'),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                shell=True)
        timer = Timer(self.task.complexity + 0.1, proc.kill)
        try:
            timer.start()
            info = os.wait4(proc.pid, 0)[2]
            time = info.ru_utime * 1000.0
            memory = info.ru_maxrss / 1024.0
            self._output, self._error = (b_string.strip() for b_string in proc.communicate(input=test, timeout=5.0))
        finally:
            timer.cancel()
        proc.kill()
        return (float(f'{time:.2f}'), float(f'{memory:.2f}'))

    def check(self):
        tests = self.task.input.split('\r\n\r\n')
        with open(f'input_{self.user.id}.txt', 'w') as file:
            file.write(tests[0])

        expected_output = self.task.output.split('\r\n\r\n')

        time = 0
        memory = 0
        output = []

        file_name = f'test_{self.user.id}'
        lang = {
            'Python': {
                'ext': '.py',
                'run': f'python {file_name}.py',
                'exec_file': f'{file_name}.py'
            },
            'C++': {
                'ext': '.cpp',
                'compile': f'g++ {file_name}.cpp -o {file_name}.out',
                'run': f'./{file_name}.out',
                'exec_file': f'{file_name}.out'
            },
            'C#': {
                'ext': '.cs',
                'compile': f'mcs -out:{file_name}.out {file_name}.cs',
                'run': f'mono {file_name}.out',
                'exec_file': f'{file_name}.out'
            },
            'Java': {
                'ext': '.java',
                'compile': f'javac {file_name}.java',
                'run': f'java {file_name}',
                'exec_file': f'{file_name}.class'
            },
            'JavaScript': {
                'ext': '.js',
                'run': f'node {file_name}.js',
                'exec_file': f'{file_name}.js'
            }
        }.get(self.language)

        if self.language == 'Java':
            self._code = self._code.replace('public class Main', f'class test_{self.user.id}')

        pre_file = file_name + lang['ext']
        exec_file = lang['exec_file']

        with open(pre_file, 'w') as file:
            file.write(self._code)

        try:
            if lang.get('compile'):
                self.run(lang['compile'])
                subprocess.run(f'rm {pre_file}', shell=True)
            else:
                self.run(lang['run'], tests[0])

            if len(self._error) and self._error.find('JAVA_TOOL_OPTIONS') == -1:
                self._status = 'System failure'
                self._message = self._error
                subprocess.run(f'rm {pre_file}', shell=True)
                return None

            for test in tests:
                with open(f'input_{self.user.id}.txt', 'w') as file:
                    file.write(test)

                current_time, current_memory = self.run(lang['run'], test)

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

        subprocess.run(f'rm {exec_file} input_{self.user.id}.txt', shell=True)

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
