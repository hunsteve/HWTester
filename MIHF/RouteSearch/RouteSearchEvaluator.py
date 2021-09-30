import sys

import Evaluator


class SearchEvaluator(Evaluator.Evaluator):
    def __init__(self, details):
        pass

    def evaluate(self, input, target_output, output, log):
        try:
            output_split = [float(distance) for distance in output.split('\t')]
            target_split = [float(distance) for distance in target_output.split('\t')]

            # check size
            if len(output_split) != len(target_split):
                return (0,
                        "Output length mismatch, should be {0}, found {1}, \nYour truncated output[:500] was: {2}".format(
                            len(output_split), len(target_split), output))

            index = 0
            for output, target in zip(output_split, target_split):
                if output < target - 0.5 or output > target + 0.5:
                    return (index, "Incorrect solution for path number {0}.".format(index))
                index += 1

            return (len(target_split), "")

        except (ValueError, OverflowError) as err:
            return (0, "{0}\nfor input:\n\n {1}".format(err.message, input))
        except:
            print sys.exc_info()[0]
            return (0, "Unknown error:\n {0} \nfor input:\n\n {1}".format(sys.exc_info()[0], input))
