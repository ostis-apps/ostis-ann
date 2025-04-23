
import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Plus, Search, FolderOpen, Clock, Calendar, FileBadge, Trash } from 'lucide-react';

// Sample project data
const projects = [
  {
    id: '1',
    name: 'Классификация документов',
    description: 'Модель для автоматической классификации документов по категориям',
    status: 'active',
    lastModified: new Date('2023-06-12'),
    modelCount: 3
  },
  {
    id: '2',
    name: 'Распознавание лиц',
    description: 'Система распознавания лиц на основе сверточных нейронных сетей',
    status: 'active',
    lastModified: new Date('2023-07-25'),
    modelCount: 2
  },
  {
    id: '3',
    name: 'Прогноз продаж',
    description: 'Модель для прогнозирования объема продаж на основе исторических данных',
    status: 'active',
    lastModified: new Date('2023-08-05'),
    modelCount: 1
  },
  {
    id: '4',
    name: 'Анализ настроения текста',
    description: 'Определение эмоциональной окраски текстовых комментариев',
    status: 'archived',
    lastModified: new Date('2023-04-18'),
    modelCount: 2
  },
  {
    id: '5',
    name: 'Обнаружение аномалий',
    description: 'Обнаружение аномальных паттернов в данных сенсоров',
    status: 'archived',
    lastModified: new Date('2023-03-10'),
    modelCount: 1
  }
];

const ProjectCard = ({ project }: { project: typeof projects[0] }) => {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between">
          <CardTitle>{project.name}</CardTitle>
          <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
            {project.status === 'active' ? 'Активный' : 'В архиве'}
          </Badge>
        </div>
        <CardDescription>{project.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>Обновлен: {project.lastModified.toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <FileBadge className="h-4 w-4 text-muted-foreground" />
            <span>Моделей: {project.modelCount}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" size="sm" className="flex items-center gap-1">
          <Trash className="h-4 w-4" />
          <span>Архивировать</span>
        </Button>
        <Button size="sm" className="flex items-center gap-1">
          <FolderOpen className="h-4 w-4" />
          <span>Открыть</span>
        </Button>
      </CardFooter>
    </Card>
  );
};

const Projects = () => {
  const activeProjects = projects.filter(p => p.status === 'active');
  const archivedProjects = projects.filter(p => p.status === 'archived');

  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Проекты</h1>
          <p className="text-muted-foreground">Управление проектами и моделями</p>
        </div>
        
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск проектов..."
              className="pl-10 max-w-md"
            />
          </div>
          
          <Button className="flex items-center gap-1">
            <Plus className="h-4 w-4" />
            <span>Новый проект</span>
          </Button>
        </div>
        
        <Tabs defaultValue="active" className="space-y-4">
          <TabsList>
            <TabsTrigger value="active" className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Активные ({activeProjects.length})
            </TabsTrigger>
            <TabsTrigger value="archived" className="flex items-center gap-1">
              <FileBadge className="h-4 w-4" />
              Архивные ({archivedProjects.length})
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="active">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {activeProjects.map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
              
              <Card className="flex flex-col items-center justify-center border-2 border-dashed p-6">
                <div className="rounded-full bg-muted p-3 mb-3">
                  <Plus className="h-6 w-6 text-muted-foreground" />
                </div>
                <h3 className="font-medium mb-1">Создать новый проект</h3>
                <p className="text-sm text-muted-foreground text-center mb-4">
                  Начните работу над новым проектом нейронной сети
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-1" />
                  Создать проект
                </Button>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="archived">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {archivedProjects.map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
};

export default Projects;
