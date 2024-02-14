from common import ScModule, ScPythonEventType
from ClassifierAnswerWriterAgent import ClassifierAnswerWriterAgent

from sc import *


class ClassifierAnswerWriterModule(ScModule):

    def __init__(self):
        ScModule.__init__(
            self,
            ctx=__ctx__,
            cpp_bridge=__cpp_bridge__,
            keynodes=[
            ],
        )

    def OnInitialize(self, params):
        print('Initialize classifier answer writer module')

        agent = ClassifierAnswerWriterAgent(self)
        ann_addr = self.ctx.HelperResolveSystemIdtf("product_quality_classifier_ann", ScType.NodeConst)
        agent.Register(ann_addr, ScPythonEventType.AddOutputEdge)

    def OnShutdown(self):
        print('Shutting down classifier answer writer module')


service = ClassifierAnswerWriterModule()
service.Run()
