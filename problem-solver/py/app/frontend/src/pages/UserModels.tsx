import { useState, useCallback, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Loader2, Layers, ChevronFirst, ChevronLast, Play, Trash2 } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { api } from '@/library/utils';
import { toast } from 'sonner';

interface UserModel {
  id: number;
  model_name: string;
  created_at: string;
}

const UserModels = () => {
  const [userModels, setUserModels] = useState<UserModel[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [selectedModelCode, setSelectedModelCode] = useState<string | null>(null);
  const [loadingModelCode, setLoadingModelCode] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Load user's saved models
  const loadUserModels = useCallback(async () => {
    if (!sessionId) return;
    
    setLoadingModels(true);
    try {
      const models = await api.getModelHistory(sessionId);
      setUserModels(models);
    } catch (err) {
      console.error('Failed to load models:', err);
      toast.error('Не удалось загрузить сохраненные модели');
    } finally {
      setLoadingModels(false);
    }
  }, [sessionId]);

  // Load specific model by ID
  const loadSpecificModel = useCallback(async (modelId: number) => {
    if (!sessionId) return;
    
    setLoadingModelCode(true);
    try {
      const model = await api.getSpecificModel(sessionId, modelId);
      if (model && model.generated_code) {
        setSelectedModelCode(model.generated_code);
      }
    } catch (err) {
      console.error('Failed to load model:', err);
      toast.error('Не удалось загрузить модель');
    } finally {
      setLoadingModelCode(false);
    }
  }, [sessionId]);

  const handleDeleteModel = async (modelId: number, modelName: string) => {
    if (!sessionId) return;
    if (!confirm('Удалить модель ?')) return;

    try {
        await api.deleteModel(modelId, sessionId);
        toast.success('Модель удалена');
        loadUserModels(); // Обновляем список
    } catch (err) {
        console.error('Failed to delete model:', err);
        toast.error('Не удалось удалить модель');
    }
  };

  // Initialize sessionId from localStorage or wherever it's stored
  useEffect(() => {
    // Try to get sessionId from localStorage or context
    const storedSessionId = localStorage.getItem('sessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      loadUserModels();
    }
    
    // Also check if we can get it from URL or context as fallback
    // This would need to be adapted based on how sessionId is actually stored
  }, [loadUserModels]);

  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <Layers className="h-8 w-8" />
            Мои модели
          </h1>
          <p className="text-muted-foreground">
            Список ваших сохраненных архитектур нейронных сетей
          </p>
        </div>

        {/* Models list section */}
        <div className="space-y-4">
          {loadingModels ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              <span>Загрузка моделей...</span>
            </div>
          ) : userModels.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">У вас пока нет сохраненных моделей</p>
              <p className="text-xs text-muted-foreground mt-2">
                Создайте и скомпилируйте модель в разделе ручной архитектуры, чтобы она появилась здесь
              </p>
              <div className="mt-4">
                <Button 
                  asChild
                  href="/architect"
                  variant="default"
                >
                  Перейти к созданию модели
                </Button>
              </div>
            </div>
          ) : (
            <>
              {userModels.map((model) => (
                <div key={model.id} className="border rounded-lg p-4 hover:border-primary/50 transition-border">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{model.model_name}</h3>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => loadSpecificModel(model.id)}
                      disabled={loadingModelCode}
                    >
                      {loadingModelCode ? (
                        <>
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Загрузка...
                        </>
                      ) : (
                        'Загрузить'
                      )}
                    </Button>
                    <Button variant="ghost" size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteModel(model.id, model.model_name);
                      }}>
                        Удалить
                        <Trash2 />
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Создано: {new Date(model.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Selected model code section */}
        {selectedModelCode && (
          <div className="mt-6">
          {selectedModelCode && (
            <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
              <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold">Сгенерированный код</h3>
                  <Button 
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedModelCode(null)}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </Button>
                </div>
                <div className="border rounded-lg p-4 bg-muted h-[500px] overflow-y-auto mb-4">
                  <pre className="whitespace-pre-wrap text-sm font-mono">{selectedModelCode}</pre>
                </div>
                <div className="flex justify-end">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(selectedModelCode);
                      toast.success('Код скопирован в буфер обмена');
                    }}
                  >
                    Копировать код
                  </Button>
                </div>
              </div>
            </div>
          )}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default UserModels;