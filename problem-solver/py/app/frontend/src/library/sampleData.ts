
import { NeuralModel, NeuralModelComparison, NeuralModelConfig } from "@/types/neural";

// Sample data for models lib
export const sampleModels: NeuralModel[] = [
  {
    id: '1',
    name: 'ResNet-50',
    description: 'Сверточная нейронная сеть для классификации изображений',
    type: 'CNN',
    tags: ['Классификация', 'Изображения', 'Предобученная'],
    accuracy: 92.1,
    parameterCount: 25600000,
    downloads: 45782,
    stars: 4.8,
    createdAt: new Date('2023-01-15')
  },
  {
    id: '2',
    name: 'BERT-base',
    description: 'Трансформер для обработки естественного языка',
    type: 'Transformer',
    tags: ['NLP', 'Текст', 'Предобученная'],
    accuracy: 89.3,
    parameterCount: 110000000,
    downloads: 34567,
    stars: 4.9,
    createdAt: new Date('2023-02-20')
  },
  {
    id: '3',
    name: 'LSTM-TimeSeries',
    description: 'Рекуррентная сеть для прогнозирования временных рядов',
    type: 'RNN',
    tags: ['Временные ряды', 'Прогнозирование', 'Финансы'],
    accuracy: 87.5,
    parameterCount: 840000,
    downloads: 12345,
    stars: 4.6,
    createdAt: new Date('2023-04-05')
  },
  {
    id: '4',
    name: 'MobileNetV3',
    description: 'Легкая сверточная сеть для мобильных устройств',
    type: 'CNN',
    tags: ['Классификация', 'Мобильные', 'Оптимизированная'],
    accuracy: 84.2,
    parameterCount: 2500000,
    downloads: 23456,
    stars: 4.5,
    createdAt: new Date('2023-03-10')
  },
  {
    id: '5',
    name: 'GPT-2 Small',
    description: 'Генеративная модель для создания текста',
    type: 'Transformer',
    tags: ['NLP', 'Генерация', 'Текст'],
    accuracy: 91.7,
    parameterCount: 124000000,
    downloads: 19876,
    stars: 4.7,
    createdAt: new Date('2023-05-12')
  },
  {
    id: '6',
    name: 'YOLOv5',
    description: 'Сеть для обнаружения объектов в реальном времени',
    type: 'CNN',
    tags: ['Обнаружение', 'Объекты', 'Реальное время'],
    accuracy: 88.6,
    parameterCount: 7500000,
    downloads: 28765,
    stars: 4.8,
    createdAt: new Date('2023-06-28')
  }
];

// Sample comparison data
export const sampleComparisonData: NeuralModelComparison[] = [
  {
    id: '1',
    name: 'ResNet-50',
    metrics: {
      accuracy: 92.1,
      precision: 90.5,
      recall: 89.8,
      f1Score: 90.1,
      trainingTime: 120,
      inferenceTime: 15,
      parameterCount: 25600000
    }
  },
  {
    id: '2',
    name: 'MobileNetV3',
    metrics: {
      accuracy: 84.2,
      precision: 83.7,
      recall: 82.9,
      f1Score: 83.3,
      trainingTime: 65,
      inferenceTime: 8,
      parameterCount: 2500000
    }
  },
  {
    id: '3',
    name: 'EfficientNetB0',
    metrics: {
      accuracy: 88.5,
      precision: 87.2,
      recall: 86.8,
      f1Score: 87.0,
      trainingTime: 95,
      inferenceTime: 12,
      parameterCount: 5300000
    }
  },
  {
    id: '4',
    name: 'VGG-16',
    metrics: {
      accuracy: 89.9,
      precision: 88.4,
      recall: 87.9,
      f1Score: 88.1,
      trainingTime: 180,
      inferenceTime: 28,
      parameterCount: 138000000
    }
  }
];

// Function to generate a sample neural network
export const generateSampleNetwork = (): NeuralModelConfig => {
  // Create nodes for each layer
  const inputNodes = Array(4).fill(0).map((_, i) => ({
    id: `input-${i}`,
    x: 50,
    y: 50 + i * 60,
    layer: 0,
    type: 'input' as const
  }));
  
  const hiddenNodes1 = Array(6).fill(0).map((_, i) => ({
    id: `hidden1-${i}`,
    x: 200,
    y: 30 + i * 50,
    layer: 1,
    type: 'hidden' as const
  }));
  
  const hiddenNodes2 = Array(5).fill(0).map((_, i) => ({
    id: `hidden2-${i}`,
    x: 350,
    y: 50 + i * 50,
    layer: 2,
    type: 'hidden' as const
  }));
  
  const outputNodes = Array(3).fill(0).map((_, i) => ({
    id: `output-${i}`,
    x: 500,
    y: 75 + i * 60,
    layer: 3,
    type: 'output' as const
  }));
  
  const allNodes = [...inputNodes, ...hiddenNodes1, ...hiddenNodes2, ...outputNodes];
  
  // Create connections between layers
  const connections = [];
  
  // Connect input to first hidden layer
  for (const inputNode of inputNodes) {
    for (const hiddenNode of hiddenNodes1) {
      connections.push({
        source: inputNode.id,
        target: hiddenNode.id,
        weight: parseFloat((Math.random() * 2 - 1).toFixed(2))
      });
    }
  }
  
  // Connect first hidden layer to second hidden layer
  for (const hiddenNode1 of hiddenNodes1) {
    for (const hiddenNode2 of hiddenNodes2) {
      connections.push({
        source: hiddenNode1.id,
        target: hiddenNode2.id,
        weight: parseFloat((Math.random() * 2 - 1).toFixed(2))
      });
    }
  }
  
  // Connect second hidden layer to output
  for (const hiddenNode of hiddenNodes2) {
    for (const outputNode of outputNodes) {
      connections.push({
        source: hiddenNode.id,
        target: outputNode.id,
        weight: parseFloat((Math.random() * 2 - 1).toFixed(2))
      });
    }
  }
  
  return {
    id: '1',
    name: 'Многослойный персептрон',
    type: 'Полносвязная нейронная сеть',
    description: 'Классификационная модель с двумя скрытыми слоями',
    layers: [
      { id: 'l1', type: 'input', neurons: 4 },
      { id: 'l2', type: 'dense', neurons: 6, activation: 'relu' },
      { id: 'l3', type: 'dense', neurons: 5, activation: 'relu' },
      { id: 'l4', type: 'output', neurons: 3, activation: 'softmax' }
    ],
    nodes: allNodes,
    connections: connections,
    parameterCount: 83,
    config: {
      optimizer: 'adam',
      learningRate: 0.001,
      batchSize: 32,
      epochs: 100,
      lossFunction: 'categorical_crossentropy',
      regularization: {
        type: 'l2',
        value: 0.001
      }
    },
    sampleCode: `import tensorflow as tf
from tensorflow import keras

# Создаем последовательную модель
model = keras.Sequential()

# Добавляем слои
model.add(keras.layers.Dense(6, activation='relu', input_shape=(4,)))
model.add(keras.layers.Dense(5, activation='relu'))
model.add(keras.layers.Dense(3, activation='softmax'))

# Компилируем модель
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Обучаем модель
history = model.fit(
    x_train, 
    y_train,
    batch_size=32,
    epochs=100,
    validation_split=0.2
)`
  };
};
