import { useState, useCallback, useMemo } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Layers, Plus, Trash2, Play, Loader2, Lightbulb, ArrowDown, ChevronFirst, ChevronLast, Image, Rows3 } from 'lucide-react';
import { api } from '@/library/utils';
import { toast } from 'sonner';

// --- Types ---

interface LayerParamField {
  key: string;
  label: string;
  description: string;
  type: 'number' | 'select';
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

interface LayerDefinition {
  value: string;
  label: string;
  category: 'input' | 'hidden' | 'output';
  params: LayerParamField[];
}

interface AddedLayer {
  id: string;
  type: string;
  label: string;
  params: Record<string, string | number>;
}

type InputMode = 'vector' | 'image';

// --- Layer definitions ---

const LAYER_DEFINITIONS: LayerDefinition[] = [
  {
    value: 'input',
    label: 'Input',
    category: 'input',
    params: [
      { key: 'size', label: 'Размер входа', description: 'Количество входных признаков', type: 'number', min: 1 },
    ],
  },
  {
    value: 'dense',
    label: 'Dense (Linear)',
    category: 'hidden',
    params: [
      { key: 'units', label: 'Нейроны', description: 'Количество нейронов в слое', type: 'number', min: 1 },
      { key: 'activation', label: 'Активация', description: 'Функция активации нейронов', type: 'select', options: ['relu', 'sigmoid', 'tanh', 'linear'] },
    ],
  },
  {
    value: 'conv2d',
    label: 'Conv2D',
    category: 'hidden',
    params: [
      { key: 'filters', label: 'Фильтры', description: 'Количество свёрточных фильтров', type: 'number', min: 1 },
      { key: 'kernel_size', label: 'Размер ядра', description: 'Сторона квадратного ядра свёртки', type: 'select', options: ['3', '5', '7'] },
      { key: 'activation', label: 'Активация', description: 'Функция активации после свёртки', type: 'select', options: ['relu', 'sigmoid', 'tanh', 'linear'] },
    ],
  },
  {
    value: 'batchnorm',
    label: 'BatchNormalization',
    category: 'hidden',
    params: [],
  },
  {
    value: 'activation',
    label: 'Activation',
    category: 'hidden',
    params: [
      { key: 'activation', label: 'Функция', description: 'Функция активации', type: 'select', options: ['relu', 'sigmoid', 'tanh', 'softmax', 'linear'] },
    ],
  },
  {
    value: 'maxpool',
    label: 'MaxPooling2D',
    category: 'hidden',
    params: [
      { key: 'pool_size', label: 'Размер пула', description: 'Размер окна для выбора максимального значения', type: 'select', options: ['2', '3'] },
    ],
  },
  {
    value: 'avgpool',
    label: 'AveragePooling2D',
    category: 'hidden',
    params: [
      { key: 'pool_size', label: 'Размер пула', description: 'Размер окна для усреднения значений', type: 'select', options: ['2', '3'] },
    ],
  },
  {
    value: 'leaky_relu',
    label: 'LeakyReLU',
    category: 'hidden',
    params: [
      { key: 'alpha', label: 'Alpha', description: 'Коэффициент утечки для отрицательных значений (0.01–1.0)', type: 'number', min: 0.01, max: 1, step: 0.05 },
    ],
  },
  {
    value: 'dropout',
    label: 'Dropout',
    category: 'hidden',
    params: [
      { key: 'rate', label: 'Доля (rate)', description: 'Доля нейронов, отключаемых при обучении (0.0–1.0)', type: 'number', min: 0, max: 1, step: 0.05 },
    ],
  },
  {
    value: 'flatten',
    label: 'Flatten',
    category: 'hidden',
    params: [],
  },
  {
    value: 'output',
    label: 'Output',
    category: 'output',
    params: [
      { key: 'units', label: 'Выходы', description: 'Количество выходных значений (классов для классификации)', type: 'number', min: 1 },
      { key: 'activation', label: 'Активация', description: 'softmax для многоклассовой, sigmoid для бинарной, linear для регрессии', type: 'select', options: ['softmax', 'sigmoid', 'linear'] },
    ],
  },
];

// --- Hints ---

const LAYER_HINTS: Record<string, string[]> = {
  input: ['Dense', 'Conv2D', 'Dropout'],
  dense: ['BatchNormalization', 'Activation', 'Dropout', 'Dense', 'Output'],
  conv2d: ['BatchNormalization', 'Activation', 'MaxPooling2D', 'AveragePooling2D', 'Dropout', 'Conv2D'],
  batchnorm: ['Activation', 'Conv2D', 'Dense', 'Dropout', 'LeakyReLU'],
  activation: ['Conv2D', 'Dense', 'MaxPooling2D', 'AveragePooling2D', 'Dropout', 'Flatten'],
  maxpool: ['Conv2D', 'Dense', 'Dropout', 'Flatten'],
  avgpool: ['Conv2D', 'Dense', 'Dropout', 'Flatten'],
  leaky_relu: ['Conv2D', 'Dense', 'MaxPooling2D', 'Dropout'],
  dropout: ['Dense', 'Conv2D', 'Activation', 'Output'],
  flatten: ['Dense', 'Dropout', 'Output'],
  output: [],
};

let layerCounter = 0;
function nextId(): string {
  layerCounter += 1;
  return `layer-${layerCounter}`;
}

// --- Neural Network SVG Visualization ---

const NEURON_COLORS: Record<string, string> = {
  input: '#22c55e',
  dense: '#3b82f6',
  conv2d: '#8b5cf6',
  batchnorm: '#f59e0b',
  activation: '#ef4444',
  maxpool: '#06b6d4',
  avgpool: '#06b6d4',
  leaky_relu: '#ef4444',
  dropout: '#6b7280',
  flatten: '#f97316',
  output: '#ef4444',
};

function NetworkVisualization({ layers }: { layers: AddedLayer[] }) {
  if (layers.length === 0) {
    return (
      <div className="h-[400px] flex items-center justify-center border-2 border-dashed rounded-md bg-muted/30">
        <div className="text-center space-y-2">
          <Layers className="h-12 w-12 mx-auto text-muted-foreground/50" />
          <p className="text-muted-foreground">Добавьте слои для построения архитектуры</p>
          <p className="text-xs text-muted-foreground">Начните с Input, закончите Output</p>
        </div>
      </div>
    );
  }

  const layerWidth = 70;
  const layerHeight = 300;
  const neuronRadius = 10;
  const neuronsPerLayer = 5;
  const gapX = 120;
  const svgWidth = Math.max(600, layers.length * gapX + 100);
  const svgHeight = layerHeight + 80;

  const layerCenters = layers.map((_, i) => 60 + i * gapX + layerWidth / 2);

  return (
    <div className="overflow-x-auto border rounded-md bg-muted/10 p-2">
      <svg width={svgWidth} height={svgHeight} className="block mx-auto">
        {/* Connection lines between layers */}
        {layers.map((_, i) => {
          if (i === layers.length - 1) return null;
          const x1 = layerCenters[i] + layerWidth / 2;
          const x2 = layerCenters[i + 1] - layerWidth / 2;
          const centerY = 40 + layerHeight / 2;
          const spread = 90;
          return (
            <g key={`conn-${i}`}>
              {Array.from({ length: neuronsPerLayer }).map((_, n) => {
                const y1 = centerY - spread / 2 + (n * spread) / (neuronsPerLayer - 1);
                return Array.from({ length: neuronsPerLayer }).map((_, m) => {
                  const y2 = centerY - spread / 2 + (m * spread) / (neuronsPerLayer - 1);
                  return (
                    <line
                      key={`line-${i}-${n}-${m}`}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#94a3b8"
                      strokeWidth={0.5}
                      opacity={0.5}
                    />
                  );
                });
              })}
            </g>
          );
        })}

        {/* Layers */}
        {layers.map((layer, i) => {
          const cx = layerCenters[i];
          const color = NEURON_COLORS[layer.type] ?? '#6b7280';
          const centerY = 40 + layerHeight / 2;
          const spread = 90;

          return (
            <g key={layer.id}>
              {/* Layer rectangle */}
              <rect
                x={cx - layerWidth / 2}
                y={40}
                width={layerWidth}
                height={layerHeight}
                rx={8}
                fill={color}
                fillOpacity={0.08}
                stroke={color}
                strokeWidth={2}
                strokeOpacity={0.6}
              />

              {/* Neurons */}
              {Array.from({ length: neuronsPerLayer }).map((_, n) => {
                const ny = centerY - spread / 2 + (n * spread) / (neuronsPerLayer - 1);
                return (
                  <circle
                    key={`neuron-${i}-${n}`}
                    cx={cx}
                    cy={ny}
                    r={neuronRadius}
                    fill={color}
                    fillOpacity={0.3}
                    stroke={color}
                    strokeWidth={2}
                  />
                );
              })}

              {/* Layer label above */}
              <text
                x={cx}
                y={28}
                textAnchor="middle"
                fontSize={12}
                fontWeight={600}
                fill={color}
              >
                {layer.label}
              </text>

              {i === layers.length - 1 && layers.length > 1 && (
                <g>
                </g>
              )}
            </g>
          );
        })}

        {/* Flow direction arrowфф */}
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
          </marker>
        </defs>
        <line
          x1={40}
          y1={svgHeight / 2}
          x2={svgWidth - 40}
          y2={svgHeight / 2}
          stroke="#94a3b8"
          strokeWidth={1}
          strokeDasharray="6 4"
          markerEnd="url(#arrowhead)"
          opacity={0.3}
        />
      </svg>
    </div>
  );
}

// --- Component ---

const ManualArchitecture = () => {
  const [layers, setLayers] = useState<AddedLayer[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogParams, setDialogParams] = useState<Record<string, string>>({});
  const [compiling, setCompiling] = useState(false);
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [generatedModelName, setGeneratedModelName] = useState<string>('ManualModel');
  const [sessionId, setSessionId] = useState<string | null>(
    () => {
      let stored = localStorage.getItem('sessionId');
      if (!stored){
        stored = crypto.randomUUID();
        localStorage.setItem('sessionId', stored)
       }
       return stored
      }
      );
  const [showModelsDialog, setShowModelsDialog] = useState(false);
  const [userModels, setUserModels] = useState<Array<{id: number; model_name: string; created_at: string}>>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [selectedModelCode, setSelectedModelCode] = useState<string | null>(null);
  const [loadingModelCode, setLoadingModelCode] = useState(false);

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

  // Input mode state
  const [inputMode, setInputMode] = useState<InputMode>('vector');
  const [imgWidth, setImgWidth] = useState('28');
  const [imgHeight, setImgHeight] = useState('28');
  const [imgChannels, setImgChannels] = useState('1');

  // Output mode state
  const [outputMode, setOutputMode] = useState<InputMode>('vector');
  const [outWidth, setOutWidth] = useState('28');
  const [outHeight, setOutHeight] = useState('28');
  const [outChannels, setOutChannels] = useState('1');

  const currentDef = LAYER_DEFINITIONS.find((d) => d.value === selectedType);
  const currentHints = selectedType ? (LAYER_HINTS[selectedType] ?? []) : [];

  const hasInput = layers.length > 0 && layers[0].type === 'input';
  const hasOutput = layers.length > 0 && layers[layers.length - 1].type === 'output';

  // Available layer types based on current state
  const availableLayers = useMemo(() => {
    const defs = LAYER_DEFINITIONS.filter((d) => d.category === 'hidden');
    if (!hasInput) {
      return [LAYER_DEFINITIONS.find((d) => d.value === 'input')!, ...defs];
    }
    if (!hasOutput) {
      return [...defs, LAYER_DEFINITIONS.find((d) => d.value === 'output')!];
    }
    return defs;
  }, [hasInput, hasOutput]);

  // Computed input size from image dimensions
  const computedInputSize = useMemo(() => {
    if (inputMode === 'image') {
      const w = parseInt(imgWidth) || 1;
      const h = parseInt(imgHeight) || 1;
      const c = parseInt(imgChannels) || 1;
      return w * h * c;
    }
    return null;
  }, [inputMode, imgWidth, imgHeight, imgChannels]);

  // --- Add layer flow ---

  const handleAddInput = () => {
    const size = inputMode === 'image' ? computedInputSize : null;
    if (inputMode === 'vector') {
      setDialogParams({ size: inputMode });
      setSelectedType('input');
      setDialogOpen(true);
      return;
    }
    // Image mode: add directly with computed size
    const w = parseInt(imgWidth) || 28;
    const h = parseInt(imgHeight) || 28;
    const c = parseInt(imgChannels) || 1;
    setLayers((prev) => [
      {
        id: nextId(),
        type: 'input',
        label: 'Input',
        params: { size: w * h * c, width: w, height: h, channels: c, mode: 'image' },
      },
    ]);
  };

  const handleAddOutput = () => {
    setSelectedType('output');
    if (outputMode === 'image') {
      const w = parseInt(outWidth) || 28;
      const h = parseInt(outHeight) || 28;
      const c = parseInt(outChannels) || 1;
      const units = w * h * c;
      setLayers((prev) => [
        ...prev,
        {
          id: nextId(),
          type: 'output',
          label: 'Output',
          params: { units, width: w, height: h, channels: c, activation: 'sigmoid', mode: 'image' },
        },
      ]);
      return;
    }
    const def = LAYER_DEFINITIONS.find((d) => d.value === 'output')!;
    const defaults: Record<string, string> = {};
    def.params.forEach((p) => {
      defaults[p.key] = p.type === 'select' && p.options ? p.options[0] : '';
    });
    setDialogParams(defaults);
    setDialogOpen(true);
  };

  const handleAddClick = () => {
    if (!currentDef) return;
    if (currentDef.params.length === 0) {
      setLayers((prev) => [...prev, { id: nextId(), type: currentDef.value, label: currentDef.label, params: {} }]);
      return;
    }
    const defaults: Record<string, string> = {};
    currentDef.params.forEach((p) => {
      defaults[p.key] = p.type === 'select' && p.options ? p.options[0] : '';
    });
    setDialogParams(defaults);
    setDialogOpen(true);
  };

  const handleDialogConfirm = () => {
    if (!currentDef) return;
    for (const field of currentDef.params) {
      const val = dialogParams[field.key];
      if (val === undefined || val === '') {
        toast.error(`Заполните поле «${field.label}»`);
        return;
      }
      if (field.type === 'number') {
        const num = Number(val);
        if (isNaN(num)) {
          toast.error(`Поле «${field.label}» должно быть числом`);
          return;
        }
        if (field.min !== undefined && num < field.min) {
          toast.error(`Поле «${field.label}» должно быть ≥ ${field.min}`);
          return;
        }
        if (field.max !== undefined && num > field.max) {
          toast.error(`Поле «${field.label}» должно быть ≤ ${field.max}`);
          return;
        }
      }
    }
    const params: Record<string, string | number> = {};
    currentDef.params.forEach((field) => {
      params[field.key] = field.type === 'number' ? Number(dialogParams[field.key]) : dialogParams[field.key];
    });

    // Insert input at beginning, output at end
    if (currentDef.value === 'input') {
      setLayers((prev) => [{ id: nextId(), type: currentDef.value, label: currentDef.label, params }, ...prev]);
    } else if (currentDef.value === 'output') {
      setLayers((prev) => [...prev, { id: nextId(), type: currentDef.value, label: currentDef.label, params }]);
    } else {
      // Insert hidden layer before output if output exists, otherwise at end
      setLayers((prev) => {
        if (hasOutput) {
          const outputLayer = prev[prev.length - 1];
          return [...prev.slice(0, -1), { id: nextId(), type: currentDef.value, label: currentDef.label, params }, outputLayer];
        }
        return [...prev, { id: nextId(), type: currentDef.value, label: currentDef.label, params }];
      });
    }

    setDialogOpen(false);
    setSelectedType('');
  };

  // --- Remove layer ---

  const handleRemove = useCallback((id: string) => {
    setLayers((prev) => prev.filter((l) => l.id !== id));
  }, []);

  const handleClear = () => setLayers([]);

  // --- Format param for table cell ---

  function formatParams(layer: AddedLayer): string {
    const entries = Object.entries(layer.params).filter(([k]) => k !== 'mode');
    if (entries.length === 0) return '—';
    return entries.map(([k, v]) => `${k}: ${v}`).join(', ');
  }

  // --- Compile ---

  const canCompile = layers.length >= 2 && hasInput && hasOutput;

   const handleCompile = async () => {
     setCompiling(true);
     try {
       const body = {
         model_name: 'ManualModel',
         layers: layers.map((l) => ({ type: l.type, params: l.params })),
       };
       const result = await api.compileManualModel(body,sessionId);
       // Store session_id and show generated code
      //  if (result.session_id) {
      //    setSessionId(result.session_id);
      //    localStorage.setItem('sessionId', result.session_id)
      //  }
       setGeneratedCode(result.generated_code);
       setGeneratedModelName(result.model_name);
       setShowCodeModal(true);
       toast.success('Модель скомпилирована');
     } catch (err: unknown) {
       const message = err instanceof Error ? err.message : 'Ошибка при компиляции';
       toast.error(message);
     } finally {
       setCompiling(false);
     }
   };

  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <Layers className="h-8 w-8" />
            Ручная архитектура
          </h1>
          <p className="text-muted-foreground">
            Визуальный конструктор архитектуры нейронной сети
          </p>
        </div>

        {/* Status badges */}
        <div className="flex items-center gap-3">
          <Badge variant={hasInput ? 'default' : 'outline'} className="gap-1">
            <ChevronFirst className="h-3 w-3" />
            {hasInput ? 'Input добавлен' : 'Добавьте Input первым'}
          </Badge>
          {layers.filter((l) => l.type !== 'input' && l.type !== 'output').length > 0 && (
            <Badge variant="secondary">
              {layers.filter((l) => l.type !== 'input' && l.type !== 'output').length} скрытых слоёв
            </Badge>
          )}
<Badge variant={hasOutput ? 'default' : 'outline'} className="gap-1">
             <ChevronLast className="h-3 w-3" />
             {hasOutput ? 'Output добавлен' : 'Добавьте Output последним'}
           </Badge>
           <Button variant="outline" size="sm" asChild>
             <a href="/user-models">
               <Layers className="h-3 w-3 mr-1" />
               Мои модели
             </a>
           </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
          {/* Панель слоёв */}
          <div className="space-y-4">
            {/* INPUT SECTION */}
            {!hasInput && (
              <Card className="border-green-500/30 bg-green-500/5">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <ChevronFirst className="h-4 w-4 text-green-600" />
                    Начальный слой (Input)
                  </CardTitle>
                  <CardDescription>Определяет форму входных данных</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <RadioGroup value={inputMode} onValueChange={(v) => setInputMode(v as InputMode)}>
                    <div className="flex items-center space-x-2 p-2 rounded-md border bg-background">
                      <RadioGroupItem value="vector" id="mode-vector" />
                      <Label htmlFor="mode-vector" className="flex items-center gap-2 cursor-pointer flex-1">
                        <Rows3 className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-sm font-medium">Вектор</div>
                          <div className="text-xs text-muted-foreground">Плоский массив признаков</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2 p-2 rounded-md border bg-background">
                      <RadioGroupItem value="image" id="mode-image" />
                      <Label htmlFor="mode-image" className="flex items-center gap-2 cursor-pointer flex-1">
                        <Image className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-sm font-medium">Изображение</div>
                          <div className="text-xs text-muted-foreground">Матрица с каналами</div>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>

                  {inputMode === 'vector' ? (
                    <div className="space-y-1.5">
                    </div>
                  ) : (
                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1.5">
                        <Label className="text-xs">Ширина</Label>
                        <Input type="number" min={1} value={imgWidth} onChange={(e) => setImgWidth(e.target.value)} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="text-xs">Высота</Label>
                        <Input type="number" min={1} value={imgHeight} onChange={(e) => setImgHeight(e.target.value)} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="text-xs">Каналы</Label>
                        <Select value={imgChannels} onValueChange={setImgChannels}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">1 (GRAY)</SelectItem>
                            <SelectItem value="3">3 (RGB)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="col-span-3 text-xs text-muted-foreground text-center">
                        Размер входа: <strong>{computedInputSize ?? '—'}</strong> ({imgWidth}×{imgHeight}×{imgChannels})
                      </div>
                    </div>
                  )}

                  <Button className="w-full" variant="default" onClick={handleAddInput}>
                    <ChevronFirst className="h-4 w-4 mr-1" />
                    Добавить Input
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* HIDDEN LAYERS SECTION */}
            {hasInput && !hasOutput && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Скрытые слои</CardTitle>
                  <CardDescription>Добавьте внутренние слои сети</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Тип слоя..." />
                    </SelectTrigger>
                    <SelectContent>
                      {LAYER_DEFINITIONS.filter((d) => d.category === 'hidden').map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button className="w-full" disabled={!selectedType} onClick={handleAddClick}>
                    <Plus className="h-4 w-4 mr-1" />
                    Добавить слой
                  </Button>

                  {currentHints.length > 0 && currentDef?.category === 'hidden' && (
                    <div className="pt-2 border-t space-y-2">
                      <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                        <Lightbulb className="h-3.5 w-3.5" />
                        Обычно после {currentDef?.label} идёт:
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {currentHints.map((hint) => (
                          <Badge key={hint} variant="secondary" className="text-xs font-normal cursor-pointer hover:bg-secondary/80"
                            onClick={() => {
                              const def = LAYER_DEFINITIONS.find((d) => d.label === hint);
                              if (def) setSelectedType(def.value);
                            }}
                          >
                            {hint}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* OUTPUT SECTION */}
            {hasInput && !hasOutput && layers.length >= 1 && (
              <Card className="border-red-500/30 bg-red-500/5">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <ChevronLast className="h-4 w-4 text-red-600" />
                    Конечный слой (Output)
                  </CardTitle>
                  <CardDescription>Завершите архитектуру выходным слоем</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <RadioGroup value={outputMode} onValueChange={(v) => setOutputMode(v as InputMode)}>
                    <div className="flex items-center space-x-2 p-2 rounded-md border bg-background">
                      <RadioGroupItem value="vector" id="mode-vector-out" />
                      <Label htmlFor="mode-vector-out" className="flex items-center gap-2 cursor-pointer flex-1">
                        <Rows3 className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-sm font-medium">Вектор</div>
                          <div className="text-xs text-muted-foreground">Плоский массив (default)</div>
                        </div>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2 p-2 rounded-md border bg-background">
                      <RadioGroupItem value="image" id="mode-image-out" />
                      <Label htmlFor="mode-image-out" className="flex items-center gap-2 cursor-pointer flex-1">
                        <Image className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-sm font-medium">Изображение</div>
                          <div className="text-xs text-muted-foreground">Матрица с каналами</div>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>

                  {outputMode === 'image' ? (
                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1.5">
                        <Label className="text-xs">Ширина</Label>
                        <Input type="number" min={1} value={outWidth} onChange={(e) => setOutWidth(e.target.value)} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="text-xs">Высота</Label>
                        <Input type="number" min={1} value={outHeight} onChange={(e) => setOutHeight(e.target.value)} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="text-xs">Каналы</Label>
                        <Select value={outChannels} onValueChange={setOutChannels}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">1 (GRAY)</SelectItem>
                            <SelectItem value="3">3 (RGB)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="col-span-3 text-xs text-muted-foreground text-center">
                        Размер выхода: <strong>{parseInt(outWidth) * parseInt(outHeight) * parseInt(outChannels)}</strong> ({outWidth}×{outHeight}×{outChannels})
                      </div>
                    </div>
                  ) : null}

                  <Button className="w-full" variant="destructive" onClick={handleAddOutput}>
                    <ChevronLast className="h-4 w-4 mr-1" />
                    Добавить Output
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Hints after output added */}
            {hasOutput && (
              <Card className="border-amber-500/30 bg-amber-500/5">
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 text-sm text-amber-700">
                    <Lightbulb className="h-4 w-4" />
                    Архитектура завершена. Можете скомпилировать или очистить.
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Info when no input yet */}
            {!hasInput && layers.length === 0 && (
              <div className="text-center text-xs text-muted-foreground p-4 border rounded-md bg-muted/20">
                <ArrowDown className="h-5 w-5 mx-auto mb-1 opacity-50" />
                Начните с добавления слоя <strong>Input</strong> выше
              </div>
            )}
          </div>

          {/* Область визуализации */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Архитектура нейронной сети</CardTitle>
              <CardDescription>
                {layers.length === 0
                  ? 'Визуализация появится после добавления слоёв'
                  : `${layers.length} слоёв`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <NetworkVisualization layers={layers} />
            </CardContent>
          </Card>
        </div>

        {/* Таблица слоёв */}
        <Card>
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base">Слои модели</CardTitle>
              <CardDescription>Список слоёв текущей архитектуры</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={layers.length === 0} onClick={handleClear}>
                <Trash2 className="h-4 w-4 mr-1" />
                Очистить
              </Button>
              <Button size="sm" disabled={!canCompile || compiling} onClick={handleCompile}>
                {compiling ? <Loader2 className="h-4 w-4 mr-1 animate-spin" /> : <Play className="h-4 w-4 mr-1" />}
                Скомпилировать
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[60px]">#</TableHead>
                  <TableHead className="w-[40px]"></TableHead>
                  <TableHead>Тип слоя</TableHead>
                  <TableHead>Параметры</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {layers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                      Добавьте слои для начала построения архитектуры
                    </TableCell>
                  </TableRow>
                ) : (
                  layers.map((layer, idx) => (
                    <TableRow key={layer.id}>
                      <TableCell className="font-medium">{idx + 1}</TableCell>
                      <TableCell>
                        {idx === 0 && layer.type === 'input' && (
                          <Badge variant="default" className="text-[10px] px-1.5 py-0">IN</Badge>
                        )}
                        {idx === layers.length - 1 && layer.type === 'output' && (
                          <Badge variant="destructive" className="text-[10px] px-1.5 py-0">OUT</Badge>
                        )}
                      </TableCell>
                      <TableCell className="font-medium">{layer.label}</TableCell>
                      <TableCell className="text-muted-foreground">{formatParams(layer)}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleRemove(layer.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
            {!canCompile && layers.length > 0 && (
              <p className="text-xs text-muted-foreground mt-2">
                {!hasInput && 'Добавьте слой Input первым. '}
                {!hasOutput && 'Добавьте слой Output последним. '}
                {layers.length < 2 && 'Минимум 2 слоя для компиляции.'}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dialog: параметры слоя */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Параметры слоя: {currentDef?.label}</DialogTitle>
            <DialogDescription>Заполните обязательные параметры</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {currentDef?.params.map((field) => (
              <div key={field.key} className="space-y-1.5">
                <Label htmlFor={`param-${field.key}`}>{field.label}</Label>
                <p className="text-xs text-muted-foreground">{field.description}</p>
                {field.type === 'number' ? (
                  <Input
                    id={`param-${field.key}`}
                    type="number"
                    min={field.min}
                    max={field.max}
                    step={field.step ?? 1}
                    value={dialogParams[field.key] ?? ''}
                    onChange={(e) => setDialogParams((prev) => ({ ...prev, [field.key]: e.target.value }))}
                    placeholder={field.label}
                  />
                ) : (
                  <Select
                    value={dialogParams[field.key] ?? ''}
                    onValueChange={(val) => setDialogParams((prev) => ({ ...prev, [field.key]: val }))}
                  >
                    <SelectTrigger id={`param-${field.key}`}>
                      <SelectValue placeholder="Выберите..." />
                    </SelectTrigger>
                    <SelectContent>
                      {field.options?.map((opt) => (
                        <SelectItem key={opt} value={opt}>
                          {opt}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setDialogOpen(false); setSelectedType(''); }}>Отмена</Button>
            <Button onClick={handleDialogConfirm}>Добавить слой</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog: список моделей пользователя */}
      <Dialog open={showModelsDialog} onOpenChange={setShowModelsDialog}>
        <DialogContent className="w-full max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Мои модели</DialogTitle>
            <DialogDescription>Список ваших сохраненных архитектур</DialogDescription>
          </DialogHeader>
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
                  Создайте и скомпилируйте модель, чтобы она появилась здесь
                </p>
              </div>
            ) : (
              <>
                {userModels.map((model) => (
                  <div key={model.id} className="border rounded-lg p-4 hover:border-primary/50 transition-border">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium">{model.model_name}</h3>
                      <Button variant="outline" size="sm" onClick={() => loadSpecificModel(model.id)}>
                        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        Загрузить
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
          {selectedModelCode && (
            <div className="mt-6">
              <DialogHeader>
                <DialogTitle>Сгенерированный код</DialogTitle>
                <DialogDescription>Код модели, готовый к использованию</DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                <div className="border rounded-lg p-4 bg-muted h-[400px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm font-mono">{selectedModelCode}</pre>
                </div>
                <div className="flex justify-end mt-2">
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
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowModelsDialog(false);
              setSelectedModelCode(null);
            }}>
              Закрыть
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
};

export default ManualArchitecture;
