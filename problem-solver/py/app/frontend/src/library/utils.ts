import {clsx, type ClassValue} from "clsx"
import {twMerge} from "tailwind-merge"
import axios, {AxiosInstance} from "axios";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

interface ChatRequest {
    question: string;
    model: string;
}

interface ChatResponse {
    answer: string;
    session_id: string;
    model: string;
}

interface FileUploadResponse {
    message: string;
    file_id: string;
}

interface FileDeleteResponse {
    message: string;
}

interface DocumentsInfo {
    id: string
    filename: string
    upload_timestamp: string
}

interface DocumentDeleteRequest {
    file_id: number;
}


const API: AxiosInstance = axios.create({
    baseURL: "http://localhost:8000",
    headers: {"Content-Type": "application/json"},
});

export const api = {

    async chat(question: string, model: string = "gemma3"): Promise<ChatResponse> {
        const payload: ChatRequest = {question, model};
        const {data} = await API.post<ChatResponse>("/chat", payload);
        return data;
    },

    async uploadDoc(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const {data} = await API.post<FileUploadResponse>(
            "/upload-doc",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }
        );
        return data;
    } catch (error: any) {
        console.error("API.uploadDoc error:", error);
        throw error;
    }
},

    async deleteDoc(fileId: number): Promise<FileDeleteResponse> {
        const payload: DocumentDeleteRequest = {file_id: fileId};

        const {data} = await API.post<FileDeleteResponse>("/delete-doc", payload);
        return data
    },

    async getFileList(): Promise<DocumentsInfo[]> {
        const {data} = await API.get<DocumentsInfo[]>("/list-docs");
        return data;
    }
};