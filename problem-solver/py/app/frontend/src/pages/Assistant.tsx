
import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import ChatInterface from '@/components/assistant/ChatInterface';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquareText, Lightbulb, BookOpen, History, Code } from 'lucide-react';

const Assistant = () => {
  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">ИИ-ассистент</h1>
          <p className="text-muted-foreground">Интеллектуальный помощник для разработки нейронных сетей</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <div className="h-[75vh]">
              <ChatInterface />
            </div>
          </div>
          
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-neural-accent" />
                  Подсказки
                </CardTitle>
                <CardDescription>Примеры запросов к ассистенту</CardDescription>
              </CardHeader>
              <CardContent className="p-4">
                <Tabs defaultValue="general">
                  <TabsList className="grid grid-cols-3">
                    <TabsTrigger value="general">Общие</TabsTrigger>
                    <TabsTrigger value="models">Модели</TabsTrigger>
                    <TabsTrigger value="code">Код</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="general" className="space-y-2 pt-2">
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Какую архитектуру выбрать для классификации изображений?
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      В чем разница между CNN и RNN?
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Как улучшить точность моей модели?
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="models" className="space-y-2 pt-2">
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Какая модель лучше для распознавания лиц?
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Создай модель для классификации новостей
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Как использовать трансферное обучение?
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="code" className="space-y-2 pt-2">
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Пример кода для сверточной сети на TensorFlow
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Как реализовать слой внимания?
                    </div>
                    <div className="text-sm p-2 rounded bg-muted/50 cursor-pointer hover:bg-muted">
                      Оптимизация гиперпараметров с помощью кода
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="h-5 w-5 text-neural-primary" />
                  История запросов
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-2">
                  <div className="text-sm p-2 rounded bg-muted/50 flex items-center justify-between">
                    <div className="truncate">О классификации текста</div>
                    <div className="text-xs text-muted-foreground">2 часа назад</div>
                  </div>
                  <div className="text-sm p-2 rounded bg-muted/50 flex items-center justify-between">
                    <div className="truncate">Сравнение RNN и LSTM</div>
                    <div className="text-xs text-muted-foreground">Вчера</div>
                  </div>
                  <div className="text-sm p-2 rounded bg-muted/50 flex items-center justify-between">
                    <div className="truncate">Архитектура трансформеров</div>
                    <div className="text-xs text-muted-foreground">3 дня назад</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-neural-secondary" />
                  Ресурсы
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-2">
                  <a href="#" className="block text-sm p-2 rounded bg-muted/50 hover:bg-muted">
                    Руководство по глубокому обучению
                  </a>
                  <a href="#" className="block text-sm p-2 rounded bg-muted/50 hover:bg-muted">
                    Документация по API
                  </a>
                  <a href="#" className="block text-sm p-2 rounded bg-muted/50 hover:bg-muted">
                    Видеоуроки
                  </a>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Assistant;
