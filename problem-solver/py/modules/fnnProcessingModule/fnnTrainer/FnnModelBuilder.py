import tensorflow as tf

from modules.fnnProcessingModule.dataClasses.TrainingParameters import TrainingParameters


def build_model(training_parameters: TrainingParameters) -> tf.keras.Model:
    model = tf.keras.models.Sequential()

    # Build implicit input layer
    input_layer_config = training_parameters.fnn_struct.layers_configuration[0]
    input_layer_input_size = input_layer_config.input_size
    input_layer = tf.keras.layers.Input(shape=(input_layer_input_size,), name='input')
    model.add(input_layer)

    # Build hidden layers
    hidden_layers_config = training_parameters.fnn_struct.layers_configuration[0: -1]
    for (i, layer_config) in enumerate(hidden_layers_config):
        if layer_config.activation_function is None or layer_config.output_size is None:
            raise ValueError("Hidden layers must have output size and activation function specified"
                             f" (layer=hidden_{i},"
                             f" activation={layer_config.activation_function},"
                             f" size={layer_config.output_size})")

        hidden_layer = tf.keras.layers.Dense(layer_config.output_size,
                                             activation=layer_config.activation_function,
                                             name=f'hidden_{i}')
        model.add(hidden_layer)

    # Build output layer
    output_layer_size = training_parameters.fnn_struct.layers_configuration[-1].output_size
    output_layer_activation_func = training_parameters.fnn_struct.layers_configuration[-1].activation_function
    output_layer = tf.keras.layers.Dense(output_layer_size,
                                         activation=output_layer_activation_func,
                                         name='output')
    model.add(output_layer)

    # Compile model and return
    # todo: configurable optimizers and metrics?
    # optimizer = tf.keras.optimizers.Adam(learning_rate=training_parameters.learning_rate)
    # optimizer = tf.train.RMSPropOptimizer(learning_rate=0.001)
    # model.compile(optimizer=optimizer, loss=tf.keras.losses.Huber(), metrics=['accuracy'])
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    model.summary()

    return model
