import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import HomePage from '../HomePage'

describe('HomePage', () => {
  it('renders the main heading', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    )
    expect(screen.getByText('Главная страница')).toBeInTheDocument()
  })

  it('renders links to submit and history pages', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    )
    expect(screen.getByText('Страница 2 - Отправка формы')).toBeInTheDocument()
    expect(screen.getByText('Страница 3 - История отправок')).toBeInTheDocument()
  })

  it('has correct href attributes for links', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    )
    const submitLink = screen.getByText('Страница 2 - Отправка формы')
    const historyLink = screen.getByText('Страница 3 - История отправок')
    
    expect(submitLink).toHaveAttribute('href', '/submit')
    expect(historyLink).toHaveAttribute('href', '/history')
  })
})

