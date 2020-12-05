from common import ScModule, ScPythonEventType
from DataProcessingAgent import DataProcessingAgent

from sc import *


class DataProcessingModule(ScModule):

    def __init__(self):
        ScModule.__init__(
            self,
            ctx=__ctx__,
            cpp_bridge=__cpp_bridge__,
            keynodes=[
            ],
        )

    def OnInitialize(self, params):
        print('Initialize data processing module')

        agent = DataProcessingAgent(self)
        ann_addr = self.ctx.HelperResolveSystemIdtf("question_run_ann", ScType.NodeConstClass)
        agent.Register(ann_addr, ScPythonEventType.AddOutputEdge)

    def OnShutdown(self):
        print('Shutting down data processing module')


service = DataProcessingModule()
service.Run()
