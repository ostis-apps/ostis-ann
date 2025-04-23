import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, BookOpen, Share2, Star } from "lucide-react";
import { cn } from '@/library/utils';
import { NeuralModel } from '@/types/neural'

interface ModelCardProps {
  model: NeuralModel;
  className?: string;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, className }) => {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{model.name}</CardTitle>
            <CardDescription className="mt-1">{model.description}</CardDescription>
          </div>
          {model.stars && (
            <div className="flex items-center gap-1 text-sm">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span>{model.stars}</span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="flex flex-wrap gap-1 mb-3">
          {model.tags.map((tag, i) => (
            <Badge key={i} variant="outline" className="bg-muted/50">{tag}</Badge>
          ))}
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-muted-foreground text-xs">Тип</p>
            <p className="font-medium">{model.type}</p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs">Точность</p>
            <p className="font-medium">{model.accuracy}%</p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs">Параметры</p>
            <p className="font-medium">{model.parameterCount.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs">Загрузки</p>
            <p className="font-medium">{model.downloads.toLocaleString()}</p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex flex-col gap-2">
        <Button variant="outline" className="w-full">
          <BookOpen className="h-4 w-4 mr-1" />
          Детали
        </Button>
        <Button variant="outline" className="w-full">
          <Share2 className="h-4 w-4 mr-1" />
          Поделиться
        </Button>
        <Button className="w-full">
          <Download className="h-4 w-4 mr-1" />
          Скачать
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ModelCard;