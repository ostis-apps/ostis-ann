
import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import ModelCard from '@/components/neural/ModelCard';
import { Search, Filter, ArrowDownAZ, ArrowUpAZ } from 'lucide-react';
import { sampleModels } from '@/library/sampleData';

const ModelLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterType, setFilterType] = useState('all');
  
  // Filter and sort models based on user selections
  const filteredModels = sampleModels
    .filter(model => {
      // Filter by search term
      const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                           model.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           model.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      // Filter by type
      const matchesType = filterType === 'all' || model.type === filterType;
      
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      // Sort models
      switch(sortBy) {
        case 'newest':
          return b.createdAt.getTime() - a.createdAt.getTime();
        case 'oldest':
          return a.createdAt.getTime() - b.createdAt.getTime();
        case 'name-asc':
          return a.name.localeCompare(b.name);
        case 'name-desc':
          return b.name.localeCompare(a.name);
        case 'popularity':
          return b.downloads - a.downloads;
        case 'accuracy':
          return b.accuracy - a.accuracy;
        default:
          return 0;
      }
    });

  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Библиотека моделей</h1>
          <p className="text-muted-foreground">Готовые и предобученные нейронные сети для различных задач</p>
        </div>
        
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск моделей..."
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex gap-2">
            <div className="w-[180px]">
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-full">
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4" />
                    <SelectValue placeholder="Тип сети" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все типы</SelectItem>
                  <SelectItem value="CNN">CNN</SelectItem>
                  <SelectItem value="RNN">RNN</SelectItem>
                  <SelectItem value="Transformer">Transformer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="w-[180px]">
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full">
                  <div className="flex items-center gap-2">
                    {sortBy.includes('asc') ? <ArrowUpAZ className="h-4 w-4" /> : <ArrowDownAZ className="h-4 w-4" />}
                    <SelectValue placeholder="Сортировка" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="newest">Сначала новые</SelectItem>
                  <SelectItem value="oldest">Сначала старые</SelectItem>
                  <SelectItem value="name-asc">По имени (А-Я)</SelectItem>
                  <SelectItem value="name-desc">По имени (Я-А)</SelectItem>
                  <SelectItem value="popularity">По популярности</SelectItem>
                  <SelectItem value="accuracy">По точности</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        
        {filteredModels.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredModels.map(model => (
              <ModelCard key={model.id} model={model} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="inline-block p-3 rounded-full bg-muted mb-4">
              <Search className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">Модели не найдены</h3>
            <p className="text-muted-foreground">
              Попробуйте изменить параметры поиска или фильтры
            </p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => {
                setSearchTerm('');
                setFilterType('all');
                setSortBy('newest');
              }}
            >
              Сбросить фильтры
            </Button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default ModelLibrary;
