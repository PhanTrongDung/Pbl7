import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

function App() {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [token, setToken] = React.useState('')
  const [question, setQuestion] = React.useState('')
  const [answer, setAnswer] = React.useState(null)
  const [error, setError] = React.useState('')
  const [loading, setLoading] = React.useState(false)

  async function login(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Đăng nhập thất bại')
      setToken(data.access_token)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  async function askQuestion(event) {
    event.preventDefault()
    if (!question.trim()) return
    setError('')
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Không thể gửi câu hỏi')
      setAnswer(data)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">PBL7 / LEGAL AI</p>
          <h1>Trợ lý pháp lý</h1>
        </div>
        <span className={`status ${token ? 'online' : ''}`}>{token ? 'Đã đăng nhập' : 'Chưa kết nối'}</span>
      </header>

      {!token ? (
        <section className="login-panel">
          <div>
            <p className="eyebrow">Secure workspace</p>
            <h2>Đăng nhập để tra cứu</h2>
            <p className="muted">Sử dụng tài khoản backend để truy cập chat và nguồn trích dẫn.</p>
          </div>
          <form onSubmit={login} className="form-stack">
            <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>Mật khẩu<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
            <button type="submit" disabled={loading}>{loading ? 'Đang xử lý...' : 'Đăng nhập'}</button>
          </form>
        </section>
      ) : (
        <section className="workspace">
          <div className="workspace-heading">
            <div><p className="eyebrow">RAG conversation</p><h2>Hỏi đáp pháp luật</h2></div>
            <button className="ghost-button" onClick={() => { setToken(''); setAnswer(null) }}>Đăng xuất</button>
          </div>
          <form onSubmit={askQuestion} className="question-box">
            <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ví dụ: Người lao động được nghỉ phép năm bao nhiêu ngày?" rows="5" />
            <button type="submit" disabled={loading}>{loading ? 'Đang truy xuất...' : 'Gửi câu hỏi'}</button>
          </form>
          {answer && <article className="answer-panel"><p className="eyebrow">Grounded answer</p><p className="answer-text">{answer.answer}</p><div className="citations"><strong>Nguồn tham khảo</strong>{answer.citations?.map((citation) => <span key={citation}>{citation}</span>)}</div></article>}
        </section>
      )}
      {error && <p className="error-message">{error}</p>}
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
