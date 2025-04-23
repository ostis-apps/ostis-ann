import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';

const Documentation = () => {
  return (
    <MainLayout>
      <div className="container mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Документация</h1>
          <p className="text-muted-foreground">Техническая документация проекта</p>
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Документация проекта</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid grid-cols-3 mb-4">
                <TabsTrigger value="overview">Обзор</TabsTrigger>
                <TabsTrigger value="architecture">Архитектура</TabsTrigger>
                <TabsTrigger value="components">Компоненты</TabsTrigger>
              </TabsList>

              <ScrollArea className="h-[70vh]">
                <TabsContent value="overview" className="space-y-4">
                  <div className="prose max-w-none">
                    <h2 className="text-2xl font-bold">1. Введение</h2>
                    <p>
                      Цель проекта — создать интеллектуальный фреймворк для помощи в разработке и изучении
                      искусственных нейронных сетей (ИНС) на первом этапе (MVP). Система должна принимать
                      вопросы пользователя по теме ИНС, извлекать релевантный контекст из внешних источников (RAG),
                      генерировать связный ответ с помощью LLM и позволять прикреплять ссылки на документы.
                    </p>
                  </div>
                </TabsContent>

                <TabsContent value="architecture" className="space-y-4">
                  <div className="prose max-w-none">
                    <h2 className="text-2xl font-bold">2. Архитектура системы</h2>

                    <h3 className="text-xl font-semibold mt-4">2.1 Контейнерная диаграмма (Этап 1)</h3>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>Frontend:</strong> React для ввода вопросов и отображения ответов.</li>
                      <li><strong>Backend API:</strong> FastAPI сервис с эндпоинтами: /chat, /upload-doc, /list-docs, /delete-doc.</li>
                      <li><strong>Vector Store:</strong> хранилище векторизованных фрагментов документов (ChromaDB).</li>
                      <li><strong>Knowledge Base:</strong> иерархическая онтология предметных областей ИНС.</li>
                      <li><strong>LLM с RAG:</strong> цепочка LangChain, объединяющая векторный и KB-контекст.</li>
                    </ul>
                  </div>
                </TabsContent>

                <TabsContent value="components" className="space-y-4">
                  <div className="prose max-w-none">
                    <h2 className="text-2xl font-bold">3. Компоненты</h2>

                    <h3 className="text-xl font-semibold mt-4">3.1 Хранилище документов</h3>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>Обработка документов:</strong> загрузка PDF/DOCX/HTML через /upload-doc, разбивка на фрагменты (ФД), сохранение оригинала и ФД.</li>
                      <li><strong>Векторизация:</strong> выбор модели (e.g., SentenceTransformers), вычисление векторов ФД; сохранение векторных представлений.</li>
                      <li><strong>База знаний:</strong> построение онтологий и ПрО, формализация понятий, привязка ФД к понятиям.</li>
                      <li><strong>Индексация:</strong> запись метаданных в СУБД, очистка временных файлов.</li>
                    </ul>

                    <h3 className="text-xl font-semibold mt-6">3.2 Составитель контекста (Context Builder)</h3>
                    <p><strong>Векторный контекст:</strong></p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Векторизация запроса пользователя.</li>
                      <li>Поиск k ближайших ФД в векторной БД.</li>
                    </ul>

                    <p className="mt-2"><strong>Контекст на основе понятий:</strong></p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Извлечение понятий из запроса (NER+онтоэкстракция).</li>
                      <li>Поиск релевантных понятий в KB, маппинг на ФД.</li>
                    </ul>

                    <p className="mt-2"><strong>Ранжирование:</strong> объединение и фильтрация ФД, удаление дублирующих фрагментов.</p>

                    <h3 className="text-xl font-semibold mt-6">3.3 LLM и пост-обработка</h3>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>RAG-генерация:</strong> отправка вопроса + объединённого контекста в LLM (OpenAI/GPT или локальный Ollama).</li>
                      <li><strong>Пост-обработка:</strong> валидация ответа, прикрепление ссылок на источники, форматирование Markdown.</li>
                      <li><strong>История диалога:</strong> хранение сессий по UUID, запись логов запросов/ответов.</li>
                    </ul>

                    <h3 className="text-xl font-semibold mt-6">3.4 Подсистема тестирования и бенчмаркинга</h3>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>Набор вопросов:</strong> вопросы теоретического и практического характера по теме ИНС.</li>
                      <li><strong>Метрики:</strong> точность ответов, время отклика, покрытие источников.</li>
                      <li><strong>CI/CD тесты:</strong> автоматизированное прогон бенчмарка при изменении кода.</li>
                    </ul>
                  </div>
                </TabsContent>
              </ScrollArea>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Documentation;
