import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const App: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState<string | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const [sessions, setSessions] = useState<any[]>([])

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
      alert('Login failed')
      return
    }
    const data = await res.json()
    setToken(data.access_token)
  }

  async function fetchUsers() {
    const res = await fetch(`${API_BASE}/users/`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setUsers(await res.json())
  }

  async function fetchSessions() {
    const res = await fetch(`${API_BASE}/sessions/`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) setSessions(await res.json())
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e2a78 0%, #5a3f9e 50%, #20e3b2 100%)',
      color: 'white',
      fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
      padding: 24
    }}>
      <h1 style={{marginBottom: 24}}>CortexAI™ Dashboard</h1>
      {!token ? (
        <div style={{maxWidth: 360, background: 'rgba(255,255,255,0.1)', padding: 16, borderRadius: 12}}>
          <h2>Login</h2>
          <input placeholder='email' value={email} onChange={e => setEmail(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
          <input type='password' placeholder='password' value={password} onChange={e => setPassword(e.target.value)} style={{width:'100%', padding:8, marginBottom:8}} />
          <button onClick={login} style={{padding:'8px 12px'}}>Login</button>
        </div>
      ) : (
        <div>
          <div style={{display:'flex', gap:16}}>
            <button onClick={fetchUsers}>Load Users</button>
            <button onClick={fetchSessions}>Load Sessions</button>
          </div>
          <div style={{marginTop:24}}>
            <h3>User Stats</h3>
            <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(users, null, 2)}</pre>
          </div>
          <div style={{marginTop:24}}>
            <h3>Sessions Chart (placeholder)</h3>
            <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(sessions, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

