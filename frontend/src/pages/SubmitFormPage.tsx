import { useState, FormEvent, ChangeEvent } from 'react'
import { Link } from 'react-router-dom'
import { submitForm, type SubmitFormRequest } from '../api'
import type { AxiosError } from 'axios'
import type { components } from '../api/types'

type SubmitFormErrorResponse = components['schemas']['SubmitFormErrorResponse']

function SubmitFormPage() {
  const [formData, setFormData] = useState<SubmitFormRequest>({
    date: '',
    first_name: '',
    last_name: '',
  })
  const [errors, setErrors] = useState<Record<string, string[]>>({})
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setErrors({})
    setSuccess(false)
    setLoading(true)

    try {
      const response = await submitForm(formData)
      if (response.success) {
        setSuccess(true)
        // Reset form
        setFormData({
          date: '',
          first_name: '',
          last_name: '',
        })
      }
    } catch (error) {
      const axiosError = error as AxiosError<SubmitFormErrorResponse>
      if (axiosError.response?.data?.error) {
        setErrors(axiosError.response.data.error)
      } else {
        setErrors({ general: ['Произошла ошибка при отправке формы'] })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Страница 2 - Отправка формы</h1>
      <Link to="/" className="link">
        ← Назад
      </Link>

      {success && (
        <div className="success-message">
          <p>Данные сохранены</p>
          <Link
            to="/history"
            className="link"
            style={{ marginTop: '10px', display: 'inline-block' }}
          >
            Перейти на Страницу 3
          </Link>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <div className="form-group">
          <label htmlFor="date">Дата *</label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
            autoComplete="off"
            data-form-type="other"
          />
          {errors.date && (
            <div className="error-message">
              {errors.date.map((msg, idx) => (
                <div key={idx}>{msg}</div>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="first_name">Имя *</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            required
            autoComplete="off"
            data-form-type="other"
          />
          {errors.first_name && (
            <div className="error-message">
              {errors.first_name.map((msg, idx) => (
                <div key={idx}>{msg}</div>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="last_name">Фамилия *</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            required
            autoComplete="off"
            data-form-type="other"
          />
          {errors.last_name && (
            <div className="error-message">
              {errors.last_name.map((msg, idx) => (
                <div key={idx}>{msg}</div>
              ))}
            </div>
          )}
        </div>

        {errors.general && (
          <div className="error-message">
            {errors.general.map((msg, idx) => (
              <div key={idx}>{msg}</div>
            ))}
          </div>
        )}

        <button type="submit" className="button" disabled={loading}>
          {loading && <span className="spinner"></span>}
          {loading ? 'Отправка...' : 'Отправить'}
        </button>
      </form>
    </div>
  )
}

export default SubmitFormPage

