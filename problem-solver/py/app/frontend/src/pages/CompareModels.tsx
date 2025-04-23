
import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { BarChartBig, LineChart, PieChart, ArrowDownToLine } from 'lucide-react';
import ComparisonChart from '@/components/compare/ComparisonChart';
import { sampleComparisonData } from '@/library/sampleData';

const CompareModels = () => {
  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Сравнение моделей</h1>
          <p className="text-muted-foreground">Сравнение производительности различных нейронных сетей</p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Выбор моделей для сравнения</CardTitle>
            <CardDescription>Выберите модели и метрики для сравнения</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium">Модели</h3>
                {['ResNet-50', 'MobileNetV3', 'EfficientNetB0', 'VGG-16'].map((model, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Checkbox id={`model-${index}`} defaultChecked />
                    <label 
                      htmlFor={`model-${index}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {model}
                    </label>
                  </div>
                ))}
                <Button variant="outline" className="w-full mt-2">Добавить модель</Button>
              </div>
              
              <div className="space-y-4">
                <h3 className="font-medium">Метрики</h3>
                {['Точность (Accuracy)', 'Полнота (Recall)', 'Точность (Precision)', 'F1-Score', 'Время обучения', 'Время вывода'].map((metric, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Checkbox id={`metric-${index}`} defaultChecked={index < 2} />
                    <label 
                      htmlFor={`metric-${index}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {metric}
                    </label>
                  </div>
                ))}
                
                <div className="pt-2">
                  <h3 className="font-medium mb-2">Набор данных</h3>
                  <Select defaultValue="imagenet">
                    <SelectTrigger>
                      <SelectValue placeholder="Выберите датасет" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="imagenet">ImageNet</SelectItem>
                      <SelectItem value="cifar10">CIFAR-10</SelectItem>
                      <SelectItem value="mnist">MNIST</SelectItem>
                      <SelectItem value="custom">Пользовательский</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Tabs defaultValue="bar" className="space-y-4">
          <div className="flex justify-between items-center">
            <TabsList>
              <TabsTrigger value="bar" className="flex items-center gap-1">
                <BarChartBig className="h-4 w-4" />
                Столбцы
              </TabsTrigger>
              <TabsTrigger value="line" className="flex items-center gap-1">
                <LineChart className="h-4 w-4" />
                Линии
              </TabsTrigger>
              <TabsTrigger value="radar" className="flex items-center gap-1">
                <PieChart className="h-4 w-4" />
                Радар
              </TabsTrigger>
            </TabsList>
            
            <Button variant="outline" className="flex items-center gap-1">
              <ArrowDownToLine className="h-4 w-4" />
              Экспорт данных
            </Button>
          </div>
          
          <TabsContent value="bar" className="space-y-6">
            <ComparisonChart 
              data={sampleComparisonData}
              metric="accuracy"
              title="Сравнение точности (Accuracy)"
              description="Показывает процент правильных предсказаний от общего числа"
            />
            
            <ComparisonChart 
              data={sampleComparisonData}
              metric="f1Score"
              title="Сравнение F1-Score"
              description="Гармоническое среднее между точностью и полнотой"
            />
            
            <ComparisonChart 
              data={sampleComparisonData}
              metric="trainingTime"
              title="Время обучения (мин)"
              description="Время, необходимое для обучения модели на заданном наборе данных"
            />
          </TabsContent>
          
          <TabsContent value="line" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Динамика точности</CardTitle>
                <CardDescription>График изменения точности в зависимости от эпох обучения</CardDescription>
              </CardHeader>
              <CardContent className="h-[400px] flex items-center justify-center border-2 border-dashed rounded-md">
                <p className="text-muted-foreground">График линий (в разработке)</p>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="radar" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Многофакторный анализ</CardTitle>
                <CardDescription>Сравнение моделей по нескольким метрикам одновременно</CardDescription>
              </CardHeader>
              <CardContent className="h-[400px] flex items-center justify-center border-2 border-dashed rounded-md">
                <p className="text-muted-foreground">Радарная диаграмма (в разработке)</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default CompareModels;
