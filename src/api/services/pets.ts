import client from '../client';
import { ApiResponse, PaginatedResponse } from '../../types/api';
import { Pet } from '../../types'; // Using existing Pet type from root for now

export const petsService = {
    getPets: (params?: any) => client.get<PaginatedResponse<Pet>>('/pets', params),
    getPetById: (id: string) => client.get<Pet>(`/pets/${id}`),
    createPet: (data: Partial<Pet>) => client.post<Pet>('/pets', data),
    updatePet: (id: string, data: Partial<Pet>) => client.put<Pet>(`/pets/${id}`, data),
    deletePet: (id: string) => client.delete<void>(`/pets/${id}`),
};
