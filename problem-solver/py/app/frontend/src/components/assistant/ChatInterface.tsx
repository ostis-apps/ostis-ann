import React, {useState, useRef, useEffect} from 'react';
import {
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle
} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {Textarea} from "@/components/ui/textarea";
import {Avatar} from "@/components/ui/avatar";
import {
    Files,
    FilePlus,
    FileMinus,
    SendHorizonal,
    BrainCircuit,
    User,
    Trash2
} from "lucide-react";
import {cn, api} from '@/library/utils';

interface Message {
    id: string;
    content: string;
    sender: 'user' | 'assistant';
    timestamp: Date;
}

interface DocumentsInfo {
    id: string;
    filename: string;
    upload_timestamp: string;
}

const LOCAL_STORAGE_KEY = "chat-messages";

const ChatInterface: React.FC = () => {
        const [messages, setMessages] = useState<Message[]>(() => {
            try {
                const saved = sessionStorage.getItem(LOCAL_STORAGE_KEY);
                if (saved) {
                    const parsed: Message[] = JSON.parse(saved);
                    return parsed.map(m => ({...m, timestamp: new Date(m.timestamp)}));
                }
            } catch {
                // ignore
            }
            return [{
                id: '1',
                content: 'Здравствуйте! Я ваш ИИ-помощник. Как я могу помочь вам сегодня?',
                sender: 'assistant',
                timestamp: new Date(),
            }];
        });

        const [inputValue, setInputValue] = useState('');
        const [isTyping, setIsTyping] = useState(false);
        const [sessionId, setSessionId] = useState<string | null>(null);

        const [files, setFiles] = useState<DocumentsInfo[]>([]);

        const [showViewFiles, setShowViewFiles] = useState(false);
        const [showDeleteFiles, setShowDeleteFiles] = useState(false);
        const [showAddFile, setShowAddFile] = useState(false);

        const fileInputRef = useRef<HTMLInputElement | null>(null);
        const viewFilesRef = useRef<HTMLUListElement | null>(null);
        const deleteFilesRef = useRef<HTMLUListElement | null>(null);
        const containerRef = useRef<HTMLDivElement | null>(null);

        useEffect(() => {
            sessionStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(messages));
        }, [messages]);

        useEffect(() => {
            const loadFiles = async () => {
                try {
                    const response = await api.getFileList();

                    setFiles(response);
                } catch (err) {
                    console.error("Ошибка загрузки файлов:", err);
                }
            };

            loadFiles();
        }, []);

        useEffect(() => {
            function handleClickOutside(event: MouseEvent) {
                const target = event.target as Node;
                if (showViewFiles && viewFilesRef.current && !viewFilesRef.current.contains(target) &&
                    !(event.target as HTMLElement).closest('#btn-view-files')) {
                    setShowViewFiles(false);
                }
                if (showDeleteFiles && deleteFilesRef.current && !deleteFilesRef.current.contains(target) &&
                    !(event.target as HTMLElement).closest('#btn-delete-files')) {
                    setShowDeleteFiles(false);
                }
                if (showAddFile && containerRef.current && !containerRef.current.contains(target) &&
                    !(event.target as HTMLElement).closest('#btn-add-file')) {
                    setShowAddFile(false);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                }
            }

            document.addEventListener('mousedown', handleClickOutside);
            return () => document.removeEventListener('mousedown', handleClickOutside);
        }, [showViewFiles, showDeleteFiles, showAddFile]);

        const handleSendMessage = async () => {
            if (!inputValue.trim()) return;

            const userMessage: Message = {
                id: Date.now().toString(),
                content: inputValue,
                sender: 'user',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, userMessage]);
            setInputValue('');
            setIsTyping(true);

            try {
                const resp = await api.chat(inputValue);
                if (!sessionId) setSessionId(resp.session_id);

                const assistantMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    content: resp.answer,
                    sender: 'assistant',
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, assistantMessage]);
            } catch (err) {
                console.error("Ошибка чата:", err);
                const errorMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    content: 'Произошла ошибка при получении ответа',
                    sender: 'assistant',
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, errorMessage]);
            } finally {
                setIsTyping(false);
            }
        };

        const handleKeyPress = (e: React.KeyboardEvent) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        };

        const toggleViewFiles = async () => {
            setFiles(await api.getFileList());
            setShowViewFiles(!showViewFiles);
            setShowDeleteFiles(false);
            setShowAddFile(false);
        };

        const toggleDeleteFiles = () => {
            setShowDeleteFiles(!showDeleteFiles);
            setShowViewFiles(false);
            setShowAddFile(false);
        };

        const handleAddFileClick = () => {
            setShowAddFile(true);
            setShowViewFiles(false);
            setShowDeleteFiles(false);
        };

        const handleAddFileCancel = () => {
            setShowAddFile(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        };

        const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
            const fileList = e.target.files;
            if (!fileList?.length) return;

            for (const file of Array.from(fileList)) {
                try {
                    const resp = await api.uploadDoc(file);
                    console.log(`Uploaded id=${resp.file_id}`, resp.message);
                } catch (err) {
                    console.error(err);
                }
            }

            try {
                 const updated = await api.getFileList();
                  setFiles(updated);
            } catch (err) {
                console.error("Не удалось обновить список файлов:", err);
            } finally {
                setShowAddFile(false);
                if (fileInputRef.current) fileInputRef.current.value = '';
            }
        };

        const handleDeleteFile = async (file: DocumentsInfo) => {
            try {
                await api.deleteDoc(Number(file.id));
                const updated = await api.getFileList();
                setFiles(updated);
            } catch (err) {
                console.error("Ошибка удаления файла:", err);
            } finally {
                setShowDeleteFiles(false);
            }
        };

        return (
            <Card className="flex flex-col h-full relative">
                <CardHeader>
                    <CardTitle
                        className="flex flex-wrap items-center gap-2 justify-between"
                    >
                        <div className="flex items-center gap-2 font-semibold text-lg shrink-0">
                            <BrainCircuit className="h-5 w-5 text-neural-accent"/>
                            ИИ-ассистент
                        </div>
                        <div className="flex gap-2 flex-wrap max-w-[65%] sm:max-w-[75%] md:max-w-[85%]">
                            {/* Button: View all files */}
                            <div className="relative">
                                <Button
                                    id="btn-view-files"
                                    variant="outline"
                                    size="sm"
                                    onClick={toggleViewFiles}
                                    aria-expanded={showViewFiles}
                                    aria-haspopup="listbox"
                                    className="flex items-center gap-1 border-neural-accent text-neural-accent hover:bg-neural-accent/10 focus:ring-1 focus:ring-neural-accent"
                                    title="Посмотреть все файлы"
                                    type="button"
                                >
                                    <Files className="w-4 h-4"/>
                                    Файлы
                                </Button>
                                {showViewFiles && (
                                    <ul
                                        ref={viewFilesRef}
                                        role="listbox"
                                        className="absolute right-0 mt-1 max-h-64 w-48 overflow-auto rounded-md border border-neural-accent bg-neural-primary/90 text-white shadow-lg z-50 backdrop-blur-sm [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-neural-accent/20 hover:[&::-webkit-scrollbar-thumb]:bg-neural-accent/30 [&::-webkit-scrollbar-horizontal]:w-2"
                                        tabIndex={-1}
                                    >
                                        {files.length === 0 && (
                                            <li className="px-3 py-2 text-neutral-400 select-none">
                                                Файлы отсутствуют
                                            </li>
                                        )}
                                        {files.map((file) => (
                                            <li
                                                key={file.filename}
                                                className="px-3 py-2 cursor-default hover:bg-neural-accent/30 rounded select-text break-words text-[0.875rem]"
                                                title={file.filename}
                                            >
                                                {file.filename}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            {/* Button: Add file */}
                            <div className="relative">
                                <Button
                                    id="btn-add-file"
                                    variant="outline"
                                    size="sm"
                                    onClick={handleAddFileClick}
                                    title="Добавить файл"
                                    className="flex items-center gap-1 border-neural-accent text-neural-accent hover:bg-neural-accent/10 focus:ring-1 focus:ring-neural-accent"
                                    type="button"
                                >
                                    <FilePlus className="w-4 h-4"/>
                                    Добавить
                                </Button>
                            </div>
                            {/* Button: Delete file */}
                            <div className="relative">
                                <Button
                                    id="btn-delete-files"
                                    variant="outline"
                                    size="sm"
                                    onClick={toggleDeleteFiles}
                                    aria-expanded={showDeleteFiles}
                                    aria-haspopup="listbox"
                                    disabled={files.length === 0}
                                    className={cn(
                                        "flex items-center gap-1 border-neural-accent text-neural-accent hover:bg-neural-accent/10 focus:ring-1 focus:ring-neural-accent",
                                        files.length === 0 ? "opacity-50 cursor-not-allowed" : ""
                                    )}
                                    title="Удалить файл"
                                    type="button"
                                >
                                    <FileMinus className="w-4 h-4"/>
                                    Удалить
                                </Button>
                                {showDeleteFiles && (
                                    <ul
                                        ref={deleteFilesRef}
                                        role="listbox"
                                        className="absolute right-0 mt-1 max-h-64 w-48 overflow-auto rounded-md border border-destructive bg-destructive/90 text-destructive-foreground shadow-lg backdrop-blur-sm z-50 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-neural-accent/20 hover:[&::-webkit-scrollbar-thumb]:bg-neural-accent/30 [&::-webkit-scrollbar-horizontal]:w-2"
                                        tabIndex={-1}
                                    >
                                        {files.length === 0 && (
                                            <li className="px-3 py-2 text-destructive-select-none">
                                                Нет файлов для удаления
                                            </li>
                                        )}
                                        {files.map((file) => (
                                            <li
                                                key={file.filename}
                                                className="px-3 py-2 cursor-pointer hover:bg-destructive-foreground hover:text-destructive rounded select-text break-words text-[0.875rem]"
                                                onClick={() => {
                                                    handleDeleteFile(file);
                                                }}
                                                role="option"
                                                tabIndex={0}
                                                title={file.filename}
                                            >
                                                {file.filename}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </CardTitle>
                </CardHeader>
                <CardContent
                    className="flex-1 overflow-auto p-4 space-y-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-neural-accent/20 hover:[&::-webkit-scrollbar-thumb]:bg-neural-accent/30 [&::-webkit-scrollbar-horizontal]:w-2">
                {messages.map((message) => (
                        <div
                            key={message.id}
                            className={cn(
                                "flex items-start gap-3 max-w-[80%]",
                                message.sender === 'user' ? "ml-auto flex-row-reverse" : ""
                            )}
                        >
                            {message.sender === 'assistant' && (
                                <Avatar className="w-8 h-8 border bg-neural-accent/20">
                                    <BrainCircuit className="h-6 w-6 text-neural-primary"/>
                                </Avatar>
                            )}
                            <div>
                                <div
                                    className={cn(
                                        "rounded-lg p-3",
                                        message.sender === 'user' ?
                                            "bg-neural-primary text-white" :
                                            "bg-muted"
                                    )}
                                >
                                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                                </p>
                            </div>
                            {message.sender === 'user' && (
                                <Avatar className="w-8 h-8 border">
                                    <User className="h-6 w-6"/>
                                </Avatar>
                            )}
                        </div>
                    ))}
                    {isTyping && (
                        <div className="flex items-start gap-3">
                            <Avatar className="w-8 h-8 border bg-neural-accent/20">
                                <BrainCircuit className="h-4 w-4 text-neural-primary"/>
                            </Avatar>
                            <div className="rounded-lg p-3 bg-muted">
                                <div className="flex space-x-1">
                                    <div className="h-2 w-2 rounded-full bg-neural-accent animate-pulse"></div>
                                    <div className="h-2 w-2 rounded-full bg-neural-accent animate-pulse delay-150"></div>
                                    <div className="h-2 w-2 rounded-full bg-neural-accent animate-pulse delay-300"></div>
                                </div>
                            </div>
                        </div>
                    )}
                </CardContent>
                <CardFooter className="border-t p-4 flex flex-col gap-2">
                    {showAddFile && (
                        <div ref={containerRef}
                             className="flex flex-col gap-2 rounded-md border border-neural-accent bg-neural-primary/90 p-3 shadow-lg max-w-sm mx-auto">
                            <div className="flex justify-between items-center">
                                <h4 className="text-sm font-semibold text-white">Добавить файл</h4>
                                <Button size="sm" variant="ghost" onClick={handleAddFileCancel}
                                        className="text-white hover:text-neutral-200 ">Отмена</Button>
                            </div>
                            <input
                                type="file"
                                multiple
                                onChange={handleFileUpload}
                                ref={fileInputRef}
                                className="file-input-bordered file-input file-input-sm w-full rounded-lg bg-neural-accent/50 hover:bg-accent-foreground/50 text-foreground"
                            />
                        </div>
                    )}
                    <div className="flex gap-2 w-full">
                        <Textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Напишите сообщение..."
                            className="flex-1 min-h-[40px] resize-none"
                            rows={1}
                            disabled={showAddFile}
                        />
                        <Button
                            onClick={handleSendMessage}
                            disabled={!inputValue.trim() || showAddFile}
                            className="shrink-0"
                        >
                            <SendHorizonal className="h-5 w-5"/>
                            <span className="sr-only">Отправить</span>
                        </Button>
                    </div>
                </CardFooter>
            </Card>
        );
    }
;

export default ChatInterface;
