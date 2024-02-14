import csv
import getpass

from common import ScResult, ScAgent, ScEventParams
from sc import *


class DataProcessingAgent(ScAgent):

    def CheckImpl(self, evt: ScEventParams) -> bool:
        ann_addr = ""
        test_file_addr = ""

        src, trg = self.module.ctx.GetEdgeInfo(evt.edge_addr)

        classifier_addr = self.module.ctx.HelperResolveSystemIdtf("product_quality_classifier_ann", ScType.NodeConst)
        rrel_1_addr = self.module.ctx.HelperResolveSystemIdtf("rrel_1", ScType.NodeConstRole)
        rrel_2_addr = self.module.ctx.HelperResolveSystemIdtf("rrel_2", ScType.NodeConstRole)

        it5_ann_1 = self.module.ctx.Iterator5(
            trg, ScType.EdgeAccessConstPosPerm, classifier_addr, ScType.EdgeAccessConstPosPerm, rrel_1_addr)
        while it5_ann_1.Next():
            ann_addr = it5_ann_1.Get(2)

        it5_ann_2 = self.module.ctx.Iterator5(
            trg, ScType.EdgeAccessConstPosPerm, ScType.NodeConst, ScType.EdgeAccessConstPosPerm, rrel_2_addr)
        while it5_ann_2.Next():
            test_file_addr = it5_ann_2.Get(2)

        if ann_addr == "" or test_file_addr == "":
            return False

        return True

    def RunImpl(self, evt: ScEventParams) -> ScResult:
        test_file_addr = ""
        test_product_addr = ""

        filename = ""
        uniformity = 0
        mass_fat_fraction = 0
        mass_protein_fraction = 0
        has_mold = 0

        src, trg = self.module.ctx.GetEdgeInfo(evt.edge_addr)
        classifier_addr = self.module.ctx.HelperResolveSystemIdtf("product_quality_classifier_ann", ScType.NodeConst)
        rrel_2_addr = self.module.ctx.HelperResolveSystemIdtf("rrel_2", ScType.NodeConstRole)
        rrel_file_addr = self.module.ctx.HelperResolveSystemIdtf("rrel_file", ScType.NodeConstRole)
        filename_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_file_name", ScType.NodeConstNoRole)
        uniformity_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_uniformity", ScType.NodeConstNoRole)
        mass_fat_fraction_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_mass_fat_fraction",
                                                                      ScType.NodeConstNoRole)
        mass_protein_fraction_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_mass_protein_fraction",
                                                                      ScType.NodeConstNoRole)
        has_mold_addr = self.module.ctx.HelperResolveSystemIdtf("nrel_has_mold", ScType.NodeConstNoRole)

        it5_ann_2 = self.module.ctx.Iterator5(
            trg, ScType.EdgeAccessConstPosPerm, ScType.NodeConst, ScType.EdgeAccessConstPosPerm, rrel_2_addr)
        while it5_ann_2.Next():
            test_file_addr = it5_ann_2.Get(2)

        it5_test_file_name = self.module.ctx.Iterator5(
            test_file_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, filename_addr)
        while it5_test_file_name.Next():
            addr2 = it5_test_file_name.Get(2)
            filename = self.module.ctx.GetLinkContent(addr2).AsString()

        if filename == "":
            print("Something went wrong. Please, make sure that filename is specified")
            return ScResult.ErrorNotFound

        it5_test_file = self.module.ctx.Iterator5(
            ScType.NodeConst, ScType.EdgeAccessConstPosPerm, test_file_addr, ScType.EdgeAccessConstPosPerm,
            rrel_file_addr)
        while it5_test_file.Next():
            test_product_addr = it5_test_file.Get(0)

        if test_product_addr == "":
            print("Something went wrong. Please, make sure that product definition is related to product file")
            return ScResult.ErrorNotFound

        it5_uniformity = self.module.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, uniformity_addr)
        while it5_uniformity.Next():
            addr2 = it5_uniformity.Get(2)
            uniformity = self.module.ctx.GetLinkContent(addr2).AsString()

        it5_mass_fat_fraction = self.module.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm,
            mass_fat_fraction_addr)
        while it5_mass_fat_fraction.Next():
            addr2 = it5_mass_fat_fraction.Get(2)
            mass_fat_fraction = self.module.ctx.GetLinkContent(addr2).AsString()

        it5_mass_protein_fraction = self.module.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm,
            mass_protein_fraction_addr)
        while it5_mass_protein_fraction.Next():
            addr2 = it5_mass_protein_fraction.Get(2)
            mass_protein_fraction = self.module.ctx.GetLinkContent(addr2).AsString()

        it5_has_mold = self.module.ctx.Iterator5(
            test_product_addr, ScType.EdgeDCommonConst, ScType.Link, ScType.EdgeAccessConstPosPerm, has_mold_addr)
        while it5_has_mold.Next():
            addr2 = it5_has_mold.Get(2)
            has_mold = self.module.ctx.GetLinkContent(addr2).AsString()

        if uniformity == 0 or mass_fat_fraction == 0 or mass_protein_fraction == 0 or has_mold == 0:
            print("Something went wrong. Please, make sure all product params are passed correctly")
            return ScResult.ErrorInvalidParams

        print('Data was successfully parsed')
        self.WriteToTsv(filename, uniformity, mass_fat_fraction, mass_protein_fraction, has_mold)

        # TODO: uncomment after fixing link content bug
        # Link for further answer processing (will be deleted afterwards)
        # self.module.ctx.CreateEdge(ScType.EdgeAccessConstPosPerm, classifier_addr, test_product_addr)
        return ScResult.Ok

    @staticmethod
    def WriteToTsv(filename, uniformity, mass_fat_fraction, mass_protein_fraction, has_mold):
        out_file = open(
            f'/home/{getpass.getuser()}/ann.ostis/api/neural_networks/product_quality_classifier/data/{filename}.tsv',
            'wt')
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['Uniformity', 'Mass fat fraction', 'Mass protein fraction', 'Has mold'])
        tsv_writer.writerow([uniformity, mass_fat_fraction, mass_protein_fraction, has_mold])
        print('Data was successfully written')
