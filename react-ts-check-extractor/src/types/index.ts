export interface UploadedFile {
    name: string;
    type: string;
    size: number;
    lastModified: number;
    file: File;
}