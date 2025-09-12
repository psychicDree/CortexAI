import React from 'react'
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const NavBar: React.FC = () => {
  return (
    <nav style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
      <Link to="/">Onboarding</Link>
      <Link to="/users">Users</Link>
      <Link to="/sessions">Sessions</Link>
      <Link to="/login">Login</Link>
    </nav>
  )
}

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e2a78 0%, #5a3f9e 50%, #20e3b2 100%)',
      color: 'white',
      fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
      padding: 24
    }}>
      <h1 style={{marginBottom: 16}}>CortexAI™ Dashboard</h1>
      <NavBar />
      {children}
    </div>
  )
}

const OnboardingPage: React.FC = () => {
  const [name, setName] = React.useState('')
  const [age, setAge] = React.useState('')
  const [result, setResult] = React.useState<string>('')

  async function submit() {
    const payload = { client_user_id: crypto.randomUUID(), display_name: name, age: Number(age) || 0 }
    const res = await fetch(`${API_BASE}/onboarding/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      setResult('Failed to submit onboarding')
      return
    }
    setResult('Onboarding submitted')
  }

  return (
    <div style={{maxWidth: 420, background: 'rgba(255,255,255,0.1)', padding: 16, borderRadius: 12}}>
      <h2>Onboarding</h2>
      <input placeholder='name' value={name} onChange={e => setName(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
      <input placeholder='age' value={age} onChange={e => setAge(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
      <button onClick={submit} style={{padding:'8px 12px'}}>Submit</button>
      <div style={{marginTop: 8}}>{result}</div>
    </div>
  )
}

const LoginPage: React.FC = () => {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [token, setToken] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string>('')

  async function login() {
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    form.set('grant_type', 'password')
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    if (!res.ok) {
      setError('Login failed')
      return
    }
    const data = await res.json()
    setToken(data.access_token)
    setError('')
  }

  return (
    <div style={{maxWidth: 360, background: 'rgba(255,255,255,0.1)', padding: 16, borderRadius: 12}}>
      <h2>Login</h2>
      <input placeholder='email' value={email} onChange={e => setEmail(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
      <input type='password' placeholder='password' value={password} onChange={e => setPassword(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
      <button onClick={login} style={{padding:'8px 12px'}}>Login</button>
      {error && <div style={{marginTop:8, color:'#ffdada'}}>{error}</div>}
      {token && <div style={{marginTop:8}}>Token acquired</div>}
    </div>
  )
}

const UsersPage: React.FC = () => {
  const [token, setToken] = React.useState<string>('')
  const [users, setUsers] = React.useState<any[]>([])
  async function fetchUsers() {
    const res = await fetch(`${API_BASE}/users/`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setUsers(await res.json())
  }
  return (
    <div>
      <div style={{display:'flex', gap:8, marginBottom:8}}>
        <input placeholder='token' value={token} onChange={e => setToken(e.target.value)} style={{width: '60%'}} />
        <button onClick={fetchUsers}>Load Users</button>
      </div>
      <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(users, null, 2)}</pre>
    </div>
  )
}

const SessionsPage: React.FC = () => {
  const [token, setToken] = React.useState<string>('')
  const [sessions, setSessions] = React.useState<any[]>([])
  async function fetchSessions() {
    const res = await fetch(`${API_BASE}/sessions/`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setSessions(await res.json())
  }
  return (
    <div>
      <div style={{display:'flex', gap:8, marginBottom:8}}>
        <input placeholder='token' value={token} onChange={e => setToken(e.target.value)} style={{width: '60%'}} />
        <button onClick={fetchSessions}>Load Sessions</button>
      </div>
      <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(sessions, null, 2)}</pre>
    </div>
  )
}

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<OnboardingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

