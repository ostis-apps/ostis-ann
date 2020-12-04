from common import ScResult, ScAgent, ScEventParams
from sc import *


class DataProcessingAgent(ScAgent):

    def RunImpl(self, evt: ScEventParams) -> ScResult:
        print("Data processing agent was initialized")
        return ScResult.Ok
