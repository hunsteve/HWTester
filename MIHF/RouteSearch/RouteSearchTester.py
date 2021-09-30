import json
import random
import sys

import Tester

reload(sys)
sys.setdefaultencoding('utf8')


def shuffled(iterable):
    perm = range(len(iterable))
    random.shuffle(perm)
    return [iterable[i] for i in perm]


class SearchTester(Tester.Tester):

    def __init__(self, details):
        super(SearchTester, self).__init__(details)

        tests_file = details["tests"]

        with open(tests_file, "r") as data_file:
            self.__tests = json.load(data_file)
        self.__break_on_first_error = details["break on first error"]
        self.__break_on_first_wrong = details["break on first wrong"]
        self.__default_timeout = details.get("default timeout") or 5.0
        self.__personal = details.get("personal") or False
        pass

    def test(self, project_name, submission):
        if submission.is_personal():
            tests = self.__tests[submission.personal_index()]
        else:
            tests = self.__tests

        for data in tests:
            timeout = self.__default_timeout
            if isinstance(data, dict):
                input = data["input"]
                target_output = data["target"]
                timeout = data.get("timeout") or self.__default_timeout
            elif isinstance(data, list):
                input = data[0]
                target_output = data[1]

            input = input + '\n'
            (stdout, stderr, extraerr) = submission.run(project_name, input, timeout=timeout)

            stdout = stdout.decode('utf-8', 'ignore').encode('ascii', 'replace').strip()
            target_output = target_output.strip()

            if not (stderr or extraerr):
                (result, message) = self.evaluator.evaluate(input, target_output, stdout, submission.log)
            else:
                result = 0
                if stderr:

                    # name = school_name.encode('utf8')
                    message = "Runtime error:\n%s\n\nfor input:\n%s" % (stderr.encode('utf8'), input.encode('utf8'))
                else:
                    message = extraerr

            submission.log.log_test(project_name, input, target_output, stdout, result, message)

            if self.__break_on_first_error and (stderr or extraerr):
                break

            if self.__break_on_first_wrong and result != 1.0:
                break
