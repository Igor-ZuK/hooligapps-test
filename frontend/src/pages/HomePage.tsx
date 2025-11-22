import { Link } from 'react-router-dom'

function HomePage() {
  return (
    <div className="page">
      <h1>Главная страница</h1>
      <div>
        <Link to="/submit" className="link">
          Страница 2 - Отправка формы
        </Link>
        <Link to="/history" className="link">
          Страница 3 - История отправок
        </Link>
      </div>
    </div>
  )
}

export default HomePage

