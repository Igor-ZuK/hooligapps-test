import axios, { AxiosError } from 'axios'
import type { components } from './types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

type SubmitFormRequest = components['schemas']['SubmitFormRequest']
type SubmitFormResponse = components['schemas']['SubmitFormResponse']
type SubmitFormErrorResponse = components['schemas']['SubmitFormErrorResponse']
type HistoryResponse = components['schemas']['HistoryResponse']
type UniqueNamesResponse = components['schemas']['UniqueNamesResponse']

export const submitForm = async (
  data: SubmitFormRequest
): Promise<SubmitFormResponse> => {
  try {
    const response = await api.post<SubmitFormResponse>('/submit', {
      date: data.date,
      first_name: data.first_name,
      last_name: data.last_name,
    })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<SubmitFormErrorResponse>
      if (axiosError.response) {
        throw axiosError
      }
    }
    throw error
  }
}

export interface HistoryFilters {
  date: string
  first_name?: string
  last_name?: string
}

export const getHistory = async (
  filters: HistoryFilters
): Promise<HistoryResponse> => {
  const params = new URLSearchParams()
  params.append('date', filters.date)
  if (filters.first_name) {
    params.append('first_name', filters.first_name)
  }
  if (filters.last_name) {
    params.append('last_name', filters.last_name)
  }

  const response = await api.get<HistoryResponse>(
    `/history?${params.toString()}`
  )
  return response.data
}

export const getUniqueNames = async (): Promise<[string[], string[]]> => {
  try {
    const response = await api.get<UniqueNamesResponse>('/unique-names')
    return [response.data.first_names || [], response.data.last_names || []]
  } catch (error) {
    console.error('Error getting unique names:', error)
    return [[], []]
  }
}

export type { SubmitFormRequest, SubmitFormResponse, HistoryResponse, UniqueNamesResponse }

