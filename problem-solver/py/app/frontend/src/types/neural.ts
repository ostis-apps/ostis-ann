
// Define types for neural network components

export interface NeuralNode {
  id: string;
  x: number;
  y: number;
  layer: number;
  type: 'input' | 'hidden' | 'output';
}

export interface NeuralConnection {
  source: string;
  target: string;
  weight: number;
}

export interface NeuralLayer {
  id: string;
  type: string;
  neurons: number;
  activation?: string;
}

export interface NeuralModelConfig {
  id: string;
  name: string;
  type: string;
  description: string;
  layers: NeuralLayer[];
  nodes: NeuralNode[];
  connections: NeuralConnection[];
  parameterCount: number;
  config: Record<string, any>;
  sampleCode: string;
}

export interface NeuralModel {
  id: string;
  name: string;
  description: string;
  type: string;
  tags: string[];
  accuracy: number;
  parameterCount: number;
  downloads: number;
  stars?: number;
  createdBy?: string;
  createdAt: Date;
}

export interface NeuralModelComparison {
  id: string;
  name: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
    trainingTime: number;
    inferenceTime: number;
    parameterCount: number;
  };
}
