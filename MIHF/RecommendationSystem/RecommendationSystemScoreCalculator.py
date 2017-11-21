import ScoreCalculator

class RecommendationSystemScoreCalculator(ScoreCalculator.ScoreCalculator):

    def __init__(self, details):
        self.__details = details
        pass

    def set_log(self, log):
        self.__log = log

    def score(self):
        ok_count = 0
        for _, results in self.__log.data["results"].iteritems():
            for result in results:
                ok_count += result["result"]

        if ok_count >= 1:
            return int(max(0, min(15.0,self.__details["score"])))
        else:
            return 0

    def message(self):
        message = []
        i = 0
        for _, results in self.__log.data["results"].iteritems():
            for result in results:
                i+=1
                message.append("%d. test result:" % i)
                message.append(result["message"])

        return "\n".join(message)