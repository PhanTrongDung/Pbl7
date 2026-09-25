import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles.css'

function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Legal AI Platform</p>
        <h1>Trợ lý pháp lý thông minh</h1>
        <p className="subtitle">
          Tra cứu, tóm tắt và phân tích văn bản pháp luật dựa trên dữ liệu đáng tin cậy.
        </p>
      </section>

      <section className="cards">
        <div className="card">
          <h3>Chat pháp lý</h3>
          <p>Hỏi đáp bằng ngôn ngữ tự nhiên với trích dẫn nguồn luật.</p>
        </div>
        <div className="card">
          <h3>Search</h3>
          <p>Tìm kiếm theo ngữ nghĩa và metadata văn bản pháp luật.</p>
        </div>
        <div className="card">
          <h3>Summary</h3>
          <p>Tóm tắt và so sánh các văn bản pháp luật liên quan.</p>
        </div>
      </section>
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
