
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Brain, Code, Settings2, Wand2 } from "lucide-react";
import { NeuralModelConfig } from '@/types/neural';
import NetworkVisualizer from './NetworkVisualizer';
import { generateSampleNetwork } from '@/library/sampleData';

const ModelGenerator: React.FC = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [generatedModel, setGeneratedModel] = useState<NeuralModelConfig | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    if (!taskDescription.trim()) return;
    
    setIsGenerating(true);
    
    // Simulate model generation with timeout
    setTimeout(() => {
      const sampleNetwork = generateSampleNetwork();
      setGeneratedModel(sampleNetwork);
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-neural-accent" />
          Генератор нейронной сети
        </CardTitle>
        <CardDescription>
          Опишите вашу задачу, и система автоматически предложит подходящую архитектуру нейронной сети
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder="Например: Классификация изображений цветов на 5 категорий с помощью сверточной нейронной сети..."
          value={taskDescription}
          onChange={(e) => setTaskDescription(e.target.value)}
          className="min-h-[100px] resize-none"
        />
        
        {generatedModel && (
          <div className="mt-6">
            <Tabs defaultValue="visual">
              <TabsList className="mb-4">
                <TabsTrigger value="visual" className="flex items-center gap-1">
                  <Brain className="h-4 w-4" />
                  Визуализация
                </TabsTrigger>
                <TabsTrigger value="config" className="flex items-center gap-1">
                  <Settings2 className="h-4 w-4" />
                  Конфигурация
                </TabsTrigger>
                <TabsTrigger value="code" className="flex items-center gap-1">
                  <Code className="h-4 w-4" />
                  Код
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="visual" className="border rounded-lg p-4 bg-muted/30">
                <h4 className="text-sm font-medium mb-2">{generatedModel.name}</h4>
                <div className="flex justify-center my-4">
                  <NetworkVisualizer
                    nodes={generatedModel.nodes}
                    connections={generatedModel.connections}
                    width={580}
                    height={300}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div className="p-3 bg-card rounded-md">
                    <p className="text-xs text-muted-foreground mb-1">Тип сети</p>
                    <p className="font-medium">{generatedModel.type}</p>
                  </div>
                  <div className="p-3 bg-card rounded-md">
                    <p className="text-xs text-muted-foreground mb-1">Слои</p>
                    <p className="font-medium">{generatedModel.layers.length}</p>
                  </div>
                  <div className="p-3 bg-card rounded-md">
                    <p className="text-xs text-muted-foreground mb-1">Параметры</p>
                    <p className="font-medium">{generatedModel.parameterCount.toLocaleString()}</p>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="config" className="border rounded-lg p-4 bg-muted/30">
                <h4 className="text-sm font-medium mb-2">Конфигурация модели</h4>
                <pre className="bg-card p-4 rounded-md text-xs overflow-x-auto">
                  {JSON.stringify(generatedModel.config, null, 2)}
                </pre>
              </TabsContent>
              
              <TabsContent value="code" className="border rounded-lg p-4 bg-muted/30">
                <h4 className="text-sm font-medium mb-2">Пример кода</h4>
                <pre className="bg-card p-4 rounded-md text-xs overflow-x-auto whitespace-pre-wrap">
                  {generatedModel.sampleCode}
                </pre>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button 
          onClick={handleGenerate} 
          disabled={!taskDescription.trim() || isGenerating}
          className="flex items-center gap-1"
        >
          <Wand2 className="h-4 w-4" />
          {isGenerating ? 'Генерация...' : 'Сгенерировать'}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ModelGenerator;
