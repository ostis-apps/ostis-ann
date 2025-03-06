import pandas as pd
import tensorflow as tf

from modules.fnnProcessingModule.dataClasses.TrainingParameters import TrainingParameters


def get_features_labels(df: pd.DataFrame, labels_column_name: str):
    # Select all columns but the labels
    # todo: this normalizes per-pixel data, but won't work properly for data with custom value ranges
    features = df.drop(labels_column_name, axis=1) / 255
    # Select only labels
    labels = df[labels_column_name].values
    return features, labels


def train_model(model: tf.keras.Model, parameters: TrainingParameters) -> None:
    labels_column = parameters.dataset_struct.labels_column

    train_features, train_labels = get_features_labels(parameters.dataset_struct.dataset, labels_column)
    train_labels_1hot = tf.keras.utils.to_categorical(train_labels)

    model.fit(
        x=train_features,
        y=train_labels_1hot,
        epochs=parameters.epochs
    )
