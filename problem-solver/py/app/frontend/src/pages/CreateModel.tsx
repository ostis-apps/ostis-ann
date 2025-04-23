
import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import ModelGenerator from '@/components/neural/ModelGenerator';
import { Brain, Layers, Code } from "lucide-react";

const CreateModel = () => {
  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Конструктор ИНС</h1>
          <p className="text-muted-foreground">Создание и настройка нейронных сетей на основе описания задачи</p>
        </div>
        
        <Tabs defaultValue="generate" className="space-y-4">
          <TabsList>
            <TabsTrigger value="generate" className="flex items-center gap-1">
              <Brain className="h-4 w-4" />
              Генерация по описанию
            </TabsTrigger>
            <TabsTrigger value="architect" className="flex items-center gap-1">
              <Layers className="h-4 w-4" />
              Ручная архитектура
            </TabsTrigger>
            <TabsTrigger value="code" className="flex items-center gap-1">
              <Code className="h-4 w-4" />
              Из кода
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="generate" className="space-y-4">
            <ModelGenerator />
          </TabsContent>
          
          <TabsContent value="architect" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Создание архитектуры вручную</CardTitle>
                <CardDescription>
                  Конструктор архитектуры нейронной сети с помощью графического интерфейса
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[400px] flex items-center justify-center border-2 border-dashed rounded-md">
                <p className="text-muted-foreground">Интерфейс визуального конструктора (в разработке)</p>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="code" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Создание из кода</CardTitle>
                <CardDescription>
                  Создайте модель, используя программный код на Python, TensorFlow или PyTorch
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[400px] flex items-center justify-center border-2 border-dashed rounded-md">
                <p className="text-muted-foreground">Интерфейс создания из кода (в разработке)</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default CreateModel;
