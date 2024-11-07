from sc_kpm import ScAgentClassic
from sc_client.models import ScAddr
from sc_kpm.sc_result import ScResult


# TODO update
class FnnInterpreterAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_interpret_fnn")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("FnnInterpreterAgent started")
        result = self.__run()
        self.logger.info("FnnInterpreterAgent finished")
        return result

    def __run(self) -> ScResult:
        return ScResult.OK
