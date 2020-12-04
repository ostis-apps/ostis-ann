from common import ScModule, ScPythonEventType
from .data_processing_agent import DataProcessingAgent

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

    def getProductAddr(self, path):
        test_product_addr = ""

        test_file_addr = self.ctx.HelperResolveSystemIdtf(path, ScType.NodeConst)
        rrel_file_addr = self.ctx.HelperResolveSystemIdtf("rrel_file", ScType.NodeConstRole)

        it5_test_file = self.ctx.Iterator5(
            ScType.NodeConst, ScType.EdgeDCommonConst, test_file_addr, ScType.EdgeAccessConstPosPerm, rrel_file_addr)
        while it5_test_file.Next():
            test_product_addr = it5_test_file.Get(0)

        return test_product_addr

    def parseInputData(self, path):
        test_product_addr = self.getProductAddr(path)
        uniformity = 0
        mass_fat_fraction = 0
        mass_protein_fraction = 0
        has_mold = 0

        uniformity_addr = self.ctx.HelperResolveSystemIdtf("nrel_uniformity", ScType.NodeConstNoRole)
        mass_fat_fraction_addr = self.ctx.HelperResolveSystemIdtf("nrel_mass_fat_fraction", ScType.NodeConstNoRole)
        mass_protein_fraction_addr = self.ctx.HelperResolveSystemIdtf("nrel_mass_protein_fraction",
                                                                      ScType.NodeConstNoRole)
        has_mold_addr = self.ctx.HelperResolveSystemIdtf("nrel_has_mold", ScType.NodeConstNoRole)

        it5_uniformity = self.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, uniformity_addr)
        while it5_uniformity.Next():
            addr2 = it5_uniformity.Get(2)
            uniformity = self.ctx.GetLinkContent(addr2).AsString()

        it5_mass_fat_fraction = self.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm,
            mass_fat_fraction_addr)
        while it5_mass_fat_fraction.Next():
            addr2 = it5_mass_fat_fraction.Get(2)
            mass_fat_fraction = self.ctx.GetLinkContent(addr2).AsString()

        it5_mass_protein_fraction = self.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm,
            mass_protein_fraction_addr)
        while it5_mass_protein_fraction.Next():
            addr2 = it5_mass_protein_fraction.Get(2)
            mass_protein_fraction = self.ctx.GetLinkContent(addr2).AsString()

        it5_has_mold = self.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, has_mold_addr)
        while it5_has_mold.Next():
            addr2 = it5_has_mold.Get(2)
            has_mold = self.ctx.GetLinkContent(addr2).AsString()

        return uniformity, mass_fat_fraction, mass_protein_fraction, has_mold

    def processAnswer(self, path, answer):
        quality_idtf = "quality_product" if answer == "GOOD" else "poor_quality_product"
        test_product_addr = self.getProductAddr(path)

        agent = DataProcessingAgent(self)
        agent.Register(test_product_addr, ScPythonEventType.AddInputEdge)
        self.ctx.CreateEdge(ScType.EdgeAccessConstPosPerm, quality_idtf, test_product_addr)

    def OnShutdown(self):
        print('Shutting down data processing module')


service = DataProcessingModule()
service.Run()
