from common import ScResult, ScAgent, ScEventParams
from sc import *


class ClassifierAnswerWriterAgent(ScAgent):

    def CheckImpl(self, evt: ScEventParams) -> bool:
        answer_addr = ""

        src, trg = self.module.ctx.GetEdgeInfo(evt.edge_addr)
        result_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_processing_result", ScType.NodeConstNoRole)

        it5 = self.module.ctx.Iterator5(
            src, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, result_addr)
        while it5.Next():
            answer_addr = it5.Get(2)

        if answer_addr == "":
            return False
        return True

    def RunImpl(self, evt: ScEventParams) -> ScResult:
        answer = ""
        test_product_addr = ""
        edge_addr = ""

        result_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_processing_result", ScType.NodeConstNoRole)

        it5 = self.module.ctx.Iterator5(
            evt.addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, result_addr)
        while it5.Next():
            addr2 = it5.Get(2)
            answer = self.module.ctx.GetLinkContent(addr2).AsString()  # Bug?

        if answer == "":
            print("Answer is not found")
            return ScResult.ErrorNotFound

        quality_idtf = "quality_product" if "GOOD" in answer else "poor_quality_product"
        print(quality_idtf)

        it3 = self.module.ctx.Iterator3(
            evt.addr, ScType.EdgeAccessConstPosPerm, ScType.NodeConst)
        while it3.Next():
            edge_addr = it3.Get(1)
            test_product_addr = it3.Get(2)

        self.module.ctx.CreateEdge(ScType.EdgeAccessConstPosPerm, quality_idtf, test_product_addr)
        print('Answer was successfully processed')

        # Clean up
        self.module.ctx.DeleteElement(edge_addr)
        return ScResult.Ok
