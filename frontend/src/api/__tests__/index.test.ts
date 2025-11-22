import { describe, it, expect, vi, beforeEach } from 'vitest'
import { submitForm, getHistory, getUniqueNames } from '../index'
import type { SubmitFormRequest } from '../index'

// Mock axios module - use hoisted to declare mocks before vi.mock()
const { mockPost, mockGet } = vi.hoisted(() => {
  return {
    mockPost: vi.fn(),
    mockGet: vi.fn(),
  }
})

vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        post: mockPost,
        get: mockGet,
      })),
      isAxiosError: (error: any) => error?.isAxiosError === true,
    },
    isAxiosError: (error: any) => error?.isAxiosError === true,
  }
})

describe('API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('submitForm', () => {
    it('sends POST request with correct data', async () => {
      const mockData: SubmitFormRequest = {
        date: '2025-01-15',
        first_name: 'Ivan',
        last_name: 'Ivanov',
      }
      const mockResponse = { data: { success: true } }
      
      mockPost.mockResolvedValue(mockResponse)
      
      const result = await submitForm(mockData)
      
      expect(mockPost).toHaveBeenCalledWith('/submit', {
        date: '2025-01-15',
        first_name: 'Ivan',
        last_name: 'Ivanov',
      })
      expect(result).toEqual({ success: true })
    })

    it('throws error on failure', async () => {
      const mockData: SubmitFormRequest = {
        date: '2025-01-15',
        first_name: 'Ivan',
        last_name: 'Ivanov',
      }
      const mockError = {
        isAxiosError: true,
        response: {
          data: {
            success: false,
            error: { first_name: ['Error'] },
          },
        },
      }
      
      mockPost.mockRejectedValue(mockError)
      
      await expect(submitForm(mockData)).rejects.toEqual(mockError)
    })
  })

  describe('getHistory', () => {
    it('sends GET request with correct query parameters', async () => {
      const filters = {
        date: '2025-01-20',
        first_name: 'Ivan',
        last_name: 'Ivanov',
      }
      const mockResponse = {
        data: {
          items: [],
          total: 0,
        },
      }
      
      mockGet.mockResolvedValue(mockResponse)
      
      const result = await getHistory(filters)
      
      expect(mockGet).toHaveBeenCalledWith(
        '/history?date=2025-01-20&first_name=Ivan&last_name=Ivanov'
      )
      expect(result).toEqual({ items: [], total: 0 })
    })
  })

  describe('getUniqueNames', () => {
    it('returns unique first and last names', async () => {
      const mockResponse = {
        data: {
          first_names: ['Ivan', 'John'],
          last_names: ['Ivanov', 'Smith'],
        },
      }
      
      mockGet.mockResolvedValue(mockResponse)
      
      const result = await getUniqueNames()
      
      expect(result).toEqual([['Ivan', 'John'], ['Ivanov', 'Smith']])
    })

    it('returns empty arrays on error', async () => {
      mockGet.mockRejectedValue(new Error('Network error'))
      
      const result = await getUniqueNames()
      
      expect(result).toEqual([[], []])
    })
  })
})

