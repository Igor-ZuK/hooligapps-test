import { useState, useEffect, ChangeEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getHistory, getUniqueNames, type HistoryFilters } from '../api'
import type { components } from '../api/types'

type HistoryItem = components['schemas']['HistoryItem']

function HistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [formData, setFormData] = useState<HistoryFilters>({
    date: searchParams.get('date') || '',
    first_name: searchParams.get('name') || searchParams.get('first_name') || '',
    last_name: searchParams.get('last_name') || '',
  })

  const [uniqueFirstNames, setUniqueFirstNames] = useState<string[]>([])
  const [uniqueLastNames, setUniqueLastNames] = useState<string[]>([])
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [_, setLoadingNames] = useState(false)

  // Load unique names on mount
  useEffect(() => {
    loadUniqueNames()
  }, [])

  // Load history if date is present in URL params on mount
  useEffect(() => {
    if (formData.date) {
      loadHistory()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Only on mount

  const loadUniqueNames = async () => {
    setLoadingNames(true)
    try {
      const [firstNames, lastNames] = await getUniqueNames()
      setUniqueFirstNames(firstNames)
      setUniqueLastNames(lastNames)
    } catch (error) {
      console.error('Error loading unique names:', error)
    } finally {
      setLoadingNames(false)
    }
  }

  const loadHistory = async () => {
    if (!formData.date) {
      return
    }

    setLoading(true)
    try {
      const response = await getHistory(formData)
      setHistory(response.items || [])
      setTotal(response.total || 0)
    } catch (error) {
      console.error('Error loading history:', error)
      alert('Ошибка при загрузке истории')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleShow = async () => {
    if (!formData.date) {
      alert('Пожалуйста, выберите дату')
      return
    }

    setLoading(true)
    try {
      const response = await getHistory(formData)
      setHistory(response.items || [])
      setTotal(response.total || 0)

      // Update URL with form values
      const params = new URLSearchParams()
      params.set('date', formData.date)
      if (formData.first_name) {
        params.set('name', formData.first_name) // Use 'name' as per requirements
      }
      if (formData.last_name) {
        params.set('last_name', formData.last_name)
      }
      setSearchParams(params)
    } catch (error) {
      console.error('Error loading history:', error)
      alert('Ошибка при загрузке истории')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Страница 3 - История отправок</h1>
      <Link to="/" className="link">
        ← Назад
      </Link>

      <div style={{ marginTop: '20px' }}>
        <h2>Фильтр</h2>
        <div className="form-group">
          <label htmlFor="date">Дата *</label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="first_name">Имя</label>
          <select
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
          >
            <option value="">Все имена</option>
            {uniqueFirstNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="last_name">Фамилия</label>
          <select
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
          >
            <option value="">Все фамилии</option>
            {uniqueLastNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          className="button"
          onClick={handleShow}
          disabled={loading || !formData.date}
        >
          {loading && <span className="spinner"></span>}
          {loading ? 'Загрузка...' : 'Показать'}
        </button>
      </div>

      {history.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Дата</th>
                <th>Имя</th>
                <th>Фамилия</th>
                <th>Количество предыдущих записей</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, idx) => (
                <tr key={idx}>
                  <td>{item.date}</td>
                  <td>{item.first_name}</td>
                  <td>{item.last_name}</td>
                  <td>{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="total-count">Всего записей: {total}</div>
        </div>
      )}

      {!loading && history.length === 0 && formData.date && (
        <div style={{ marginTop: '20px', color: '#666' }}>Записи не найдены</div>
      )}
    </div>
  )
}

export default HistoryPage

