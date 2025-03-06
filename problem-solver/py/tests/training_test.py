import pandas as pd
from sc_client.models import ScAddr

from modules.fnnProcessingModule.fnnTrainer.FnnModelBuilder import build_model
from modules.fnnProcessingModule.fnnTrainer.FnnTrainer import train_model
from modules.fnnProcessingModule.dataClasses.DatasetStruct import DatasetStruct
from modules.fnnProcessingModule.dataClasses.FnnLayerConfiguration import FnnLayerConfiguration
from modules.fnnProcessingModule.dataClasses.FnnStruct import FnnStruct
from modules.fnnProcessingModule.dataClasses.TrainingParameters import TrainingParameters

dataset = pd.read_csv('D:/work/OSTIS/ostis-ann/kb/fnn_processing_module/datasets/fashion_mnist_train.csv')
labels_column = 'label'

batch_size = 64
epochs = 4
learning_rate = 0.001

inp_conf: FnnLayerConfiguration = FnnLayerConfiguration(address=ScAddr(),
                                                        input_size=784,
                                                        output_size=30,
                                                        activation_function='relu')
hidden_conf: FnnLayerConfiguration = FnnLayerConfiguration(address=ScAddr(),
                                                           input_size=None,
                                                           output_size=20,
                                                           activation_function='relu')
out_conf: FnnLayerConfiguration = FnnLayerConfiguration(address=ScAddr(),
                                                        input_size=None,
                                                        output_size=10,
                                                        activation_function='softmax')


conf = (inp_conf, hidden_conf, out_conf)

params: TrainingParameters = TrainingParameters(FnnStruct(None, conf),
                                                DatasetStruct(dataset, labels_column),
                                                epochs,
                                                learning_rate,
                                                batch_size)

model = build_model(params)

train_model(model, params)
