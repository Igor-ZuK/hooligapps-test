import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import SubmitFormPage from '../SubmitFormPage'
import * as api from '../../api'
import type { AxiosError } from 'axios'

// Mock the API
vi.mock('../../api', () => ({
  submitForm: vi.fn(),
}))

describe('SubmitFormPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form with all fields', () => {
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    expect(screen.getByLabelText('Дата *')).toBeInTheDocument()
    expect(screen.getByLabelText('Имя *')).toBeInTheDocument()
    expect(screen.getByLabelText('Фамилия *')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /отправить/i })).toBeInTheDocument()
  })

  it('allows user to fill in the form', async () => {
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    const dateInput = screen.getByLabelText('Дата *')
    const firstNameInput = screen.getByLabelText('Имя *')
    const lastNameInput = screen.getByLabelText('Фамилия *')
    
    await user.type(dateInput, '2025-01-15')
    await user.type(firstNameInput, 'Ivan')
    await user.type(lastNameInput, 'Ivanov')
    
    expect(dateInput).toHaveValue('2025-01-15')
    expect(firstNameInput).toHaveValue('Ivan')
    expect(lastNameInput).toHaveValue('Ivanov')
  })

  it('submits form with correct data', async () => {
    const user = userEvent.setup()
    vi.mocked(api.submitForm).mockResolvedValue({ success: true })
    
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    await user.type(screen.getByLabelText('Дата *'), '2025-01-15')
    await user.type(screen.getByLabelText('Имя *'), 'Ivan')
    await user.type(screen.getByLabelText('Фамилия *'), 'Ivanov')
    await user.click(screen.getByRole('button', { name: /отправить/i }))
    
    await waitFor(() => {
      expect(api.submitForm).toHaveBeenCalledWith({
        date: '2025-01-15',
        first_name: 'Ivan',
        last_name: 'Ivanov',
      })
    })
  })

  it('shows success message after successful submission', async () => {
    const user = userEvent.setup()
    vi.mocked(api.submitForm).mockResolvedValue({ success: true })
    
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    await user.type(screen.getByLabelText('Дата *'), '2025-01-15')
    await user.type(screen.getByLabelText('Имя *'), 'Ivan')
    await user.type(screen.getByLabelText('Фамилия *'), 'Ivanov')
    await user.click(screen.getByRole('button', { name: /отправить/i }))
    
    await waitFor(() => {
      expect(screen.getByText('Данные сохранены')).toBeInTheDocument()
    })
  })

  it('displays validation errors', async () => {
    const user = userEvent.setup()
    const error = {
      isAxiosError: true,
      response: {
        data: {
          error: {
            first_name: ['No whitespace in first_name is allowed'],
          },
        },
      },
    } as AxiosError
    vi.mocked(api.submitForm).mockRejectedValue(error)
    
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    await user.type(screen.getByLabelText('Дата *'), '2025-01-15')
    await user.type(screen.getByLabelText('Имя *'), 'Ivan Ivanov')
    await user.type(screen.getByLabelText('Фамилия *'), 'Ivanov')
    await user.click(screen.getByRole('button', { name: /отправить/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/No whitespace in first_name is allowed/i)).toBeInTheDocument()
    })
  })

  it('shows loading state during submission', async () => {
    const user = userEvent.setup()
    let resolvePromise: (value: any) => void
    const promise = new Promise((resolve) => {
      resolvePromise = resolve
    })
    // @ts-ignore
      vi.mocked(api.submitForm).mockReturnValue(promise)
    
    render(
      <BrowserRouter>
        <SubmitFormPage />
      </BrowserRouter>
    )
    
    await user.type(screen.getByLabelText('Дата *'), '2025-01-15')
    await user.type(screen.getByLabelText('Имя *'), 'Ivan')
    await user.type(screen.getByLabelText('Фамилия *'), 'Ivanov')
    
    // Get button before clicking (when it says "Отправить")
    const submitButton = screen.getByRole('button', { name: /отправить/i })
    
    // Click the button
    await user.click(submitButton)
    
    // After click, button text changes to "Отправка..." and button is disabled
    await waitFor(() => {
      expect(submitButton).toHaveTextContent(/отправка/i)
      expect(submitButton).toBeDisabled()
    })
    
    // Resolve the promise to clean up
    resolvePromise!({ success: true })
    await waitFor(() => {
      expect(submitButton).not.toHaveTextContent(/отправка/i)
    })
  })
})

