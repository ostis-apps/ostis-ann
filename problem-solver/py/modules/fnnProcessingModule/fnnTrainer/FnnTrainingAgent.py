import sc_kpm
from sc_client.client import create_elements
from sc_client.constants import sc_types
from sc_client.models import ScAddr, ScConstruction, ScLinkContentType, ScLinkContent
from sc_kpm import ScAgentClassic
from sc_kpm.sc_result import ScResult
from sc_kpm.utils import get_system_idtf

from .FnnModelBuilder import build_model
from .FnnTrainer import train_model
from .TrainingParametersReader import TrainingParametersReader, get_ann_path
from ..dataClasses.TrainingParameters import TrainingParameters


class FnnTrainingAgent(ScAgentClassic):
    def __init__(self) -> None:
        super().__init__("action_train_fnn")

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr) -> ScResult:
        self.logger.info("FnnTrainingAgent started")
        result = self.__run(action_element)
        self.logger.info("FnnTrainingAgent finished")
        return result

    def __run(self, action_element: ScAddr) -> ScResult:
        # Get training parameters from input struct
        reader = TrainingParametersReader()
        training_parameters = reader.get_training_params(action_element)

        # Build model
        model = build_model(training_parameters)

        # Train model
        train_model(model, training_parameters)

        # Write trained network to memory
        self.__save_model(model, training_parameters)

        # todo: error handling
        return ScResult.OK

    def __save_model(self, model, training_parameters: TrainingParameters) -> None:
        ann_path = get_ann_path()
        trained_models_path = f'{ann_path}/kb/fnn_processing_module/trained_models'

        fnn_idtf = get_system_idtf(training_parameters.fnn_struct.network_address)
        trained_model_filepath = f'{trained_models_path}/{fnn_idtf}.keras'

        self.__save_model_to_file(model, trained_model_filepath)
        self.__save_model_to_sc_memory(trained_model_filepath, training_parameters.fnn_struct.network_address)

    @staticmethod
    def __save_model_to_file(model, filepath) -> None:
        model.save(filepath)

    @staticmethod
    def __save_model_to_sc_memory(filepath, fnn_addr: ScAddr) -> None:
        construction = ScConstruction()

        # todo: some garbage is being stored in link instead of provided filepath string
        #  client bug?
        link_content = ScLinkContent(filepath, ScLinkContentType.STRING)
        construction.create_link(sc_types.LINK_CONST, link_content, 'link')

        construction.create_edge(sc_types.EDGE_D_COMMON_CONST,
                                 fnn_addr,
                                 'link',
                                 'edge')
        construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,
                                 sc_kpm.ScKeynodes["nrel_trained_model_filepath"],
                                 'edge')

        addresses = create_elements(construction)
        assert len(addresses) == 3
        assert all(addresses)
