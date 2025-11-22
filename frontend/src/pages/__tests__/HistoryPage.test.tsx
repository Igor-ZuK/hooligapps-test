import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import HistoryPage from '../HistoryPage'
import * as api from '../../api'

// Mock the API
vi.mock('../../api', () => ({
  getHistory: vi.fn(),
  getUniqueNames: vi.fn(),
}))

describe('HistoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.getUniqueNames).mockResolvedValue([['Ivan', 'John'], ['Ivanov', 'Smith']])
  })

  it('renders the filter form', () => {
    render(
      <BrowserRouter>
        <HistoryPage />
      </BrowserRouter>
    )
    
    expect(screen.getByLabelText('Дата *')).toBeInTheDocument()
    expect(screen.getByLabelText('Имя')).toBeInTheDocument()
    expect(screen.getByLabelText('Фамилия')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /показать/i })).toBeInTheDocument()
  })

  it('loads unique names on mount', async () => {
    render(
      <BrowserRouter>
        <HistoryPage />
      </BrowserRouter>
    )
    
    await waitFor(() => {
      expect(api.getUniqueNames).toHaveBeenCalled()
    })
  })

  it('displays history table when data is loaded', async () => {
    const user = userEvent.setup()
    const mockHistory = {
      items: [
        {
          date: '2025-01-15',
          first_name: 'Ivan',
          last_name: 'Ivanov',
          count: 0,
        },
      ],
      total: 1,
    }
    vi.mocked(api.getHistory).mockResolvedValue(mockHistory)
    
    render(
      <BrowserRouter>
        <HistoryPage />
      </BrowserRouter>
    )
    
    await user.type(screen.getByLabelText('Дата *'), '2025-01-20')
    await user.click(screen.getByRole('button', { name: /показать/i }))
    
    await waitFor(() => {
      // Use more specific selectors to avoid conflicts with select options
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'Ivan' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'Ivanov' })).toBeInTheDocument()
      expect(screen.getByText('Всего записей: 1')).toBeInTheDocument()
    })
  })

  it('shows empty state when no history found', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getHistory).mockResolvedValue({ items: [], total: 0 })
    
    render(
      <BrowserRouter>
        <HistoryPage />
      </BrowserRouter>
    )
    
    const dateInput = screen.getByLabelText('Дата *')
    await user.clear(dateInput)
    await user.type(dateInput, '2025-01-20')
    await user.click(screen.getByRole('button', { name: /показать/i }))
    
    await waitFor(() => {
      expect(screen.getByText('Записи не найдены')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('filters by first name when selected', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getHistory).mockResolvedValue({ items: [], total: 0 })
    
    render(
      <BrowserRouter>
        <HistoryPage />
      </BrowserRouter>
    )
    
    // Wait for unique names to load
    await waitFor(() => {
      expect(api.getUniqueNames).toHaveBeenCalled()
    })
    
    const dateInput = screen.getByLabelText('Дата *')
    await user.clear(dateInput)
    await user.type(dateInput, '2025-01-20')
    
    // Use fireEvent to change select value
    const firstNameSelect = screen.getByLabelText('Имя')
    fireEvent.change(firstNameSelect, { target: { value: 'Ivan' } })
    
    await user.click(screen.getByRole('button', { name: /показать/i }))
    
    await waitFor(() => {
      expect(api.getHistory).toHaveBeenCalledWith(
        expect.objectContaining({
          date: '2025-01-20',
          first_name: 'Ivan',
        })
      )
    })
  })
})

