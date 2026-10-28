import { createContext, useContext, useEffect, useState } from 'react'
import { Link, NavLink, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import {
  ArrowDownUp, ArrowRight, BookOpen, Check, ChevronRight, Copy, FileKey2,
  Fingerprint, KeyRound, LockKeyhole, ShieldCheck, Sparkles, UnlockKeyhole,
  Upload, X, Eye, EyeOff,
} from 'lucide-react'
import { api, copyText, saveTextFile } from './api.js'

const RSAContext = createContext(null)
const navGroups = [
  {
    label: 'TASK 1 · CLASSICAL + SYMMETRIC',
    items: [
      { to: '/task-1', label: 'Overview', icon: BookOpen, end: true },
      { to: '/caesar', label: 'Caesar Cipher', icon: ArrowDownUp },
      { to: '/aes', label: 'AES-128-GCM', icon: LockKeyhole },
    ],
  },
  {
    label: 'TASK 2 · PUBLIC KEY',
    items: [
      { to: '/task-2', label: 'Overview', icon: BookOpen, end: true },
      { to: '/rsa/keys', label: 'Key Generation', icon: KeyRound },
      { to: '/rsa/encrypt', label: 'RSA Encryption', icon: LockKeyhole },
      { to: '/rsa/decrypt', label: 'RSA Decryption', icon: UnlockKeyhole },
      { to: '/rsa/demo', label: 'Numerical Demo', icon: Fingerprint },
    ],
  },
  {
    label: 'REFERENCE',
    items: [{ to: '/compare', label: 'Compare Algorithms', icon: ArrowDownUp }, { to: '/learn', label: 'How it works', icon: BookOpen }],
  },
]

function App() {
  const [rsa, setRsa] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('cryptolab-rsa-session')) || { keyId: '', publicKey: '', bits: 0 } }
    catch { return { keyId: '', publicKey: '', bits: 0 } }
  })
  useEffect(() => {
    try {
      if (rsa.keyId) sessionStorage.setItem('cryptolab-rsa-session', JSON.stringify(rsa))
      else sessionStorage.removeItem('cryptolab-rsa-session')
    } catch { /* Session storage may be disabled; current-tab use still works. */ }
  }, [rsa])
  return (
    <RSAContext.Provider value={{ rsa, setRsa }}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/task-1" element={<TaskOverview task={1} />} />
          <Route path="/caesar" element={<CaesarPage />} />
          <Route path="/aes" element={<AESPage />} />
          <Route path="/task-2" element={<TaskOverview task={2} />} />
          <Route path="/rsa/keys" element={<RSAKeysPage />} />
          <Route path="/rsa/encrypt" element={<RSAEncryptPage />} />
          <Route path="/rsa/decrypt" element={<RSADecryptPage />} />
          <Route path="/rsa/demo" element={<RSADemoPage />} />
          <Route path="/learn" element={<LearningPage />} />
          <Route path="/compare" element={<ComparisonPage />} />
          <Route path="*" element={<Home />} />
        </Route>
      </Routes>
    </RSAContext.Provider>
  )
}

function Layout() {
  const location = useLocation()
  const [apiOnline, setApiOnline] = useState(false)
  useEffect(() => {
    api('/health').then(() => setApiOnline(true)).catch(() => setApiOnline(false))
  }, [location.pathname])
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark"><ShieldCheck size={19} /></span>
          <span>cipher<span className="brand-light">lab</span></span>
        </Link>
        <div className="topbar-right">
          <span className="project-label">CRYPTOGRAPHY LEARNING TOOLKIT</span>
          <span className={`api-status ${apiOnline ? 'online' : 'offline'}`}><span />{apiOnline ? 'API online' : 'API offline'}</span>
        </div>
      </header>
      <div className="body-shell">
        <aside className="sidebar">
          <div className="sidebar-caption">WORKSPACE</div>
          <NavLink to="/" end className={({ isActive }) => `side-link ${isActive ? 'active' : ''}`}>
            <Sparkles size={16} /><span>Dashboard</span>
          </NavLink>
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="sidebar-caption">{group.label}</div>
              {group.items.map(({ to, label, icon: Icon, end }) => (
                <NavLink key={to} to={to} end={end} className={({ isActive }) => `side-link ${isActive ? 'active' : ''}`}>
                  <Icon size={16} strokeWidth={1.8} /><span>{label}</span>
                </NavLink>
              ))}
            </div>
          ))}
          <div className="sidebar-note"><ShieldCheck size={15} /><span>Educational use only</span></div>
        </aside>
        <main className="main-area"><Outlet /></main>
      </div>
      <footer className="footer"><span>CRYPTOLAB</span><span>Built for learning · Use trusted libraries for all cryptographic operations</span><span>COLLEGE PROJECT</span></footer>
    </div>
  )
}

function PageHeader({ eyebrow, title, description, icon: Icon }) {
  return (
    <div className="page-header">
      <div className="page-icon">{Icon ? <Icon size={20} /> : <Fingerprint size={20} />}</div>
      <div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>
    </div>
  )
}

function Status({ type = 'success', children, onClose }) {
  if (!children) return null
  const Icon = type === 'error' ? X : Check
  return <div className={`status status-${type}`} role={type === 'error' ? 'alert' : 'status'}><Icon size={16} /><span>{children}</span>{onClose && <button className="icon-button" aria-label="Dismiss" onClick={onClose}><X size={15} /></button>}</div>
}

function OutputBox({ label, value, language, onCopy, copyLabel = 'Copy' }) {
  const [copied, setCopied] = useState(false)
  if (value === undefined || value === null) return null
  const copy = async () => {
    try { await copyText(value); setCopied(true); setTimeout(() => setCopied(false), 1500); onCopy?.() }
    catch { setCopied(false) }
  }
  return (
    <div className="output-wrap">
      <div className="output-top"><span>{label}</span><button className="text-button" onClick={copy}><Copy size={14} />{copied ? 'Copied' : copyLabel}</button></div>
      <pre className={`output-box ${language || ''}`}>{value}</pre>
    </div>
  )
}

function Home() {
  return <div className="page-content home-page">
    <div className="hero">
      <div className="eyebrow"><span className="eyebrow-line" /> CRYPTOGRAPHY · LEARNING ENVIRONMENT</div>
      <h1>Understand the<br /><span>science of secrecy.</span></h1>
      <p>Explore classical and modern encryption through working demonstrations. Learn what happens to a message at every step.</p>
      <div className="hero-meta"><span><span className="dot-live" /> 4 ALGORITHMS</span><span>2 ASSIGNMENT TRACKS</span><span>INTERACTIVE DEMOS</span></div>
    </div>
    <div className="section-heading"><div><div className="eyebrow">YOUR ASSIGNMENTS</div><h2>Choose a learning track</h2></div><span className="section-index">01 — 02</span></div>
    <div className="track-grid">
      <Link className="track-card task-one" to="/task-1">
        <div className="track-top"><span className="track-number">TASK 01</span><span className="track-icon"><ArrowDownUp size={20} /></span></div>
        <h3>Classical &amp;<br />Symmetric Encryption</h3>
        <p>From letter substitution to authenticated encryption. Explore shared-key approaches across two eras.</p>
        <div className="track-tags"><span>CAESAR CIPHER</span><span>AES-128-GCM</span></div>
        <div className="track-open">Explore track <ArrowRight size={16} /></div>
      </Link>
      <Link className="track-card task-two" to="/task-2">
        <div className="track-top"><span className="track-number">TASK 02</span><span className="track-icon"><KeyRound size={20} /></span></div>
        <h3>Public-Key<br />Cryptography</h3>
        <p>See how public and private key pairs make secure communication possible without a shared secret.</p>
        <div className="track-tags"><span>RSA-OAEP</span><span>KEY MANAGEMENT</span></div>
        <div className="track-open">Explore track <ArrowRight size={16} /></div>
      </Link>
    </div>
    <div className="home-bottom"><div className="home-bottom-icon"><ShieldCheck size={19} /></div><div><strong>Safe by design, built for learning.</strong><p>Modern encryption runs on PyCryptodome. No keys or passwords are written into the project files.</p></div><Link to="/learn">Read the guide <ChevronRight size={15} /></Link></div>
  </div>
}

function TaskOverview({ task }) {
  const isOne = task === 1
  const items = isOne
    ? [{ to: '/caesar', icon: ArrowDownUp, name: 'Caesar Cipher', text: 'A shift substitution cipher to understand the fundamentals of encryption.', meta: 'CLASSICAL · SYMMETRIC' }, { to: '/aes', icon: LockKeyhole, name: 'AES-128-GCM', text: 'Authenticated encryption with a password-derived key and a portable payload.', meta: 'MODERN · SYMMETRIC' }]
    : [{ to: '/rsa/keys', icon: KeyRound, name: 'RSA Key Generation', text: 'Create a secure 2048-bit or 3072-bit public/private key pair.', meta: 'KEY MANAGEMENT' }, { to: '/rsa/encrypt', icon: LockKeyhole, name: 'RSA-OAEP Encryption', text: 'Encrypt short messages with a public key and SHA-256 OAEP padding.', meta: 'PUBLIC-KEY ENCRYPTION' }, { to: '/rsa/decrypt', icon: UnlockKeyhole, name: 'RSA-OAEP Decryption', text: 'Recover text with the matching private key.', meta: 'PRIVATE-KEY DECRYPTION' }, { to: '/rsa/demo', icon: Fingerprint, name: 'Numerical Example', text: 'Walk through the small-number textbook calculation by hand.', meta: 'EDUCATIONAL ONLY' }]
  return <div className="page-content">
    <PageHeader eyebrow={`ASSIGNMENT TASK 0${task}`} title={isOne ? 'Classical & Symmetric Encryption' : 'Public-Key Cryptography'} description={isOne ? 'Compare a simple historical cipher with modern authenticated encryption.' : 'Explore public/private key workflows and the math behind RSA.'} icon={isOne ? ArrowDownUp : KeyRound} />
    <div className="algorithm-grid">{items.map(({ to, icon: Icon, name, text, meta }, index) => <Link className="algorithm-card" to={to} key={name}><div className="algorithm-card-head"><span className="algorithm-card-icon"><Icon size={19} /></span><span className="algorithm-card-num">0{index + 1}</span></div><span className="eyebrow">{meta}</span><h3>{name}</h3><p>{text}</p><div className="algorithm-link">Open tool <ArrowRight size={15} /></div></Link>)}</div>
    <div className="note-panel"><BookOpen size={18} /><p>{isOne ? 'Task 1 algorithms use a shared secret: the same key or passphrase is needed to encrypt and decrypt.' : 'Keep the real RSA-OAEP implementation separate from the tiny textbook arithmetic example. The example values are intentionally insecure.'}</p></div>
  </div>
}

function CaesarPage() {
  const [text, setText] = useState('HELLO')
  const [shift, setShift] = useState(3)
  const [cipher, setCipher] = useState('')
  const [decrypted, setDecrypted] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const run = async (mode) => {
    setError(''); setCipher(''); setDecrypted('')
    if (!text.length) { setError('Enter text before running the cipher.'); return }
    if (!Number.isInteger(shift) || shift < 0 || shift > 25) { setError('Shift must be a whole number from 0 to 25.'); return }
    setBusy(true)
    try {
      const { result } = await api(`/caesar/${mode}`, { text, shift: Number(shift) })
      if (mode === 'encrypt') { setCipher(result); const roundTrip = await api('/caesar/decrypt', { text: result, shift: Number(shift) }); setDecrypted(roundTrip.result) }
      else { setCipher(text); setDecrypted(result) }
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const reset = () => { setText(''); setCipher(''); setDecrypted(''); setShift(3); setError('') }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 01 / CLASSICAL CIPHER" title="Caesar Cipher" description="A simple substitution cipher. Each English letter shifts by a fixed number of places." icon={ArrowDownUp} />
    <div className="workspace-grid">
      <section className="panel"><div className="panel-title"><div><span className="eyebrow">MESSAGE INPUT</span><h2>Choose your text</h2></div><button className="text-button" onClick={() => { setText('HELLO'); setShift(3); setError(''); setCipher(''); setDecrypted('') }}>Load example</button></div>
        <label className="field-label" htmlFor="caesar-text">Plaintext or ciphertext</label><textarea id="caesar-text" rows="6" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type or paste your message…" />
        <div className="field-row"><label className="field-label" htmlFor="caesar-shift">Shift key</label><div className="range-value">{shift}<span> / 25</span></div></div>
        <input id="caesar-shift" className="range-input" type="range" min="0" max="25" step="1" value={shift} onChange={(e) => setShift(Number(e.target.value))} />
        <div className="number-field"><input aria-label="Shift key value" type="number" min="0" max="25" step="1" value={shift} onChange={(e) => setShift(e.target.value === '' ? '' : Number(e.target.value))} /><span>Letters wrap around at Z</span></div>
        <div className="button-row"><button className="button-primary" disabled={busy} onClick={() => run('encrypt')}>{busy ? 'Working…' : <><LockKeyhole size={16} /> Encrypt</>}</button><button className="button-secondary" disabled={busy} onClick={() => run('decrypt')}><UnlockKeyhole size={16} /> Decrypt</button><button className="button-quiet" onClick={reset}>Clear</button></div>
        <Status type="error">{error}</Status>
      </section>
      <section className="panel result-panel"><div className="eyebrow">RESULTS</div><h2>Output</h2>{cipher ? <><OutputBox label="CIPHERTEXT" value={cipher} /><OutputBox label="DECRYPTED RESULT" value={decrypted} /></> : <div className="empty-result"><span><ArrowDownUp size={20} /></span><strong>Your output appears here</strong><p>Enter a message and choose Encrypt or Decrypt to see the result.</p></div>}
        <div className="formula-card"><div className="eyebrow">THE FORMULA</div><div className="formula-row"><span>Encrypt</span><code>E(x) = (x + k) mod 26</code></div><div className="formula-row"><span>Decrypt</span><code>D(x) = (x − k) mod 26</code></div><p>Uppercase and lowercase stay intact. Numbers, punctuation, spaces, emoji, and other characters pass through unchanged.</p></div>
      </section>
    </div>
    <div className="warning-strip"><span className="warning-mark">!</span><span>Caesar is easily broken by trying all 26 shifts. It is included for learning, never for protecting real information.</span></div>
  </div>
}

function AESPage() {
  const [mode, setMode] = useState('encrypt')
  const [plaintext, setPlaintext] = useState('')
  const [password, setPassword] = useState('')
  const [visible, setVisible] = useState(false)
  const [payload, setPayload] = useState('')
  const [recovered, setRecovered] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)
  const runEncrypt = async () => {
    setError(''); setSuccess(''); setPayload(''); setRecovered('')
    if (!plaintext.length) return setError('Enter a message before encrypting.')
    if (!password) return setError('Enter a passphrase before encrypting.')
    setBusy(true)
    try { const result = await api('/aes/encrypt', { plaintext, password }); setPayload(result.payload); setSuccess('Message encrypted and authenticated successfully.') }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const runDecrypt = async () => {
    setError(''); setSuccess(''); setRecovered('')
    if (!payload.trim()) return setError('Paste an AES payload before decrypting.')
    if (!password) return setError('Enter the passphrase used for encryption.')
    setBusy(true)
    try { const result = await api('/aes/decrypt', { payload, password }); setRecovered(result.plaintext); setSuccess('Authentication passed. The original message was recovered.') }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const reset = () => { setPlaintext(''); setPassword(''); setPayload(''); setRecovered(''); setError(''); setSuccess(''); setMode('encrypt') }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 01 / MODERN SYMMETRIC" title="AES-128-GCM" description="Authenticated encryption that protects both your message and its integrity." icon={LockKeyhole} />
    <div className="crypto-info"><div className="crypto-info-icon"><ShieldCheck size={18} /></div><div><strong>Confidentiality + authentication</strong><p>AES-GCM encrypts the message and checks that the ciphertext has not been altered. A new random salt and nonce are created for every encryption.</p></div><span className="crypto-badge">AES · 128 BIT</span></div>
    <div className="tabs"><button className={mode === 'encrypt' ? 'tab active' : 'tab'} onClick={() => { setMode('encrypt'); setError(''); setSuccess('') }}><LockKeyhole size={15} /> Encrypt</button><button className={mode === 'decrypt' ? 'tab active' : 'tab'} onClick={() => { setMode('decrypt'); setError(''); setSuccess('') }}><UnlockKeyhole size={15} /> Decrypt</button><button className="tab-reset" onClick={reset}>Clear / Reset</button></div>
    <div className="panel aes-panel">
      {mode === 'encrypt' ? <><div className="panel-title"><div><span className="eyebrow">ENCRYPT A MESSAGE</span><h2>Protect your text</h2></div><span className="small-lock"><LockKeyhole size={16} /></span></div>
        <label className="field-label" htmlFor="aes-plaintext">Plaintext</label><textarea id="aes-plaintext" rows="5" value={plaintext} onChange={(e) => setPlaintext(e.target.value)} placeholder="Type a message. Unicode is supported — for example, नमस्ते 🔐" />
        <label className="field-label" htmlFor="aes-password">Passphrase</label><div className="password-field"><input id="aes-password" type={visible ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Choose a passphrase" autoComplete="new-password" /><button aria-label={visible ? 'Hide passphrase' : 'Show passphrase'} onClick={() => setVisible(!visible)}>{visible ? <EyeOff size={16} /> : <Eye size={16} />}</button></div>
        <div className="helper-text">Your passphrase is used to derive a 128-bit key with PBKDF2-HMAC-SHA-256. It is never stored.</div>
        <button className="button-primary wide-button" disabled={busy} onClick={runEncrypt}>{busy ? 'Encrypting…' : <><LockKeyhole size={16} /> Encrypt with AES-128-GCM</>}</button>
        {payload && <OutputBox label="ENCRYPTED PAYLOAD · COPY THE ENTIRE VALUE" value={payload} />}
      </> : <><div className="panel-title"><div><span className="eyebrow">DECRYPT A PAYLOAD</span><h2>Recover your text</h2></div><span className="small-lock"><UnlockKeyhole size={16} /></span></div>
        <label className="field-label" htmlFor="aes-payload">Encrypted payload</label><textarea id="aes-payload" rows="6" value={payload} onChange={(e) => setPayload(e.target.value)} placeholder="Paste the complete CLT1: payload here…" />
        <label className="field-label" htmlFor="aes-password-decrypt">Passphrase</label><div className="password-field"><input id="aes-password-decrypt" type={visible ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter the original passphrase" autoComplete="current-password" /><button aria-label={visible ? 'Hide passphrase' : 'Show passphrase'} onClick={() => setVisible(!visible)}>{visible ? <EyeOff size={16} /> : <Eye size={16} />}</button></div>
        <button className="button-primary wide-button" disabled={busy} onClick={runDecrypt}>{busy ? 'Verifying…' : <><UnlockKeyhole size={16} /> Decrypt and verify</>}</button>
        {recovered && <OutputBox label="RECOVERED PLAINTEXT" value={recovered} />}
      </>}
      <Status type="error">{error}</Status><Status>{success}</Status>
    </div>
    <div className="payload-note"><span className="eyebrow">PAYLOAD FORMAT</span><p><code>CLT1:</code> version prefix + Base64 URL-safe JSON containing the KDF name, iteration count, random salt, GCM nonce, ciphertext, and authentication tag. Keep the passphrase separate from the payload.</p></div>
  </div>
}

function RSAKeysPage() {
  const { rsa, setRsa } = useContext(RSAContext)
  const [bits, setBits] = useState(2048)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [confirmed, setConfirmed] = useState(false)
  const [exportPassword, setExportPassword] = useState('')
  const [privateExport, setPrivateExport] = useState('')
  const generate = async () => {
    setBusy(true); setError(''); setStatus(''); setPrivateExport('')
    try { const result = await api('/rsa/keys', { bits }); setRsa({ keyId: result.key_id, publicKey: result.public_key, bits: result.bits }); setStatus(`Generated a ${result.bits}-bit RSA key pair. The private key remains in backend memory.`) }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const exportKey = async () => {
    setError(''); setStatus('')
    if (!confirmed) return setError('Confirm that you understand the private key must remain secret.')
    if (exportPassword.length < 8) return setError('Use an export password of at least 8 characters.')
    try { const result = await api('/rsa/export-private', { key_id: rsa.keyId, password: exportPassword }); setPrivateExport(result.private_key); setStatus('An encrypted PKCS#8 private key is ready to download. Keep the export password separate.') }
    catch (e) { setError(e.message) }
  }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 02 / KEY MANAGEMENT" title="RSA Key Generation" description="Create a public/private key pair using a trusted cryptographic library." icon={KeyRound} />
    <div className="key-grid">
      <section className="panel"><div className="panel-title"><div><span className="eyebrow">GENERATE A PAIR</span><h2>Choose key strength</h2></div><span className="small-lock"><KeyRound size={17} /></span></div>
        <label className="field-label" htmlFor="rsa-bits">RSA key size</label><select id="rsa-bits" value={bits} onChange={(e) => setBits(Number(e.target.value))}><option value={2048}>2048 bits · recommended for this demo</option><option value={3072}>3072 bits · stronger, slower</option></select>
        <div className="key-explain"><div><span className="key-symbol public">PUB</span><div><strong>Public key</strong><small>Share it with anyone who needs to encrypt a message to you.</small></div></div><div><span className="key-symbol private">PRV</span><div><strong>Private key</strong><small>Keep it secret. It decrypts messages for the matching public key.</small></div></div></div>
        <button className="button-primary wide-button" disabled={busy} onClick={generate}>{busy ? 'Generating secure keys…' : <><Sparkles size={16} /> Generate key pair</>}</button>
        <Status type="error">{error}</Status><Status>{status}</Status>
      </section>
      <section className="panel"><div className="panel-title"><div><span className="eyebrow">ACTIVE KEY PAIR</span><h2>{rsa.keyId ? `${rsa.bits}-bit keys ready` : 'No keys generated'}</h2></div><span className="key-ready"><span className={rsa.keyId ? 'dot-live' : 'dot-muted'} />{rsa.keyId ? 'IN MEMORY' : 'EMPTY'}</span></div>
        {rsa.publicKey ? <><OutputBox label="PUBLIC KEY · PEM" value={rsa.publicKey} /><button className="button-secondary wide-button" onClick={() => saveTextFile('cryptolab-public-key.pem', rsa.publicKey)}><Upload size={15} /> Download public key</button>
          <div className="export-private"><div className="eyebrow">OPTIONAL PRIVATE-KEY EXPORT</div><p>Export only if needed. The file is password-protected with encrypted PKCS#8.</p><label className="check-row"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /><span>I understand the private key must be kept secret.</span></label><label className="field-label" htmlFor="export-pass">Export password</label><input id="export-pass" type="password" value={exportPassword} onChange={(e) => setExportPassword(e.target.value)} placeholder="At least 8 characters" autoComplete="new-password" /><button className="button-secondary" disabled={!confirmed} onClick={exportKey}><FileKey2 size={15} /> Prepare protected export</button>{privateExport && <button className="button-danger" onClick={() => saveTextFile('cryptolab-private-key-encrypted.pem', privateExport)}><Upload size={15} /> Download encrypted private key</button>}<button className="button-quiet" onClick={() => { setConfirmed(false); setExportPassword(''); setPrivateExport(''); setError(''); setStatus('') }}>Reset export form</button></div>
        </> : <div className="empty-result compact"><span><KeyRound size={20} /></span><strong>Generate to see the public key</strong><p>Private key material stays on the local backend process.</p></div>}
      </section>
    </div>
    <div className="warning-strip"><span className="warning-mark">!</span><span>Never share the private key or its password. Generated key material is held in this backend process and disappears when it stops.</span></div>
  </div>
}

function RSAEncryptPage() {
  const { rsa } = useContext(RSAContext)
  const [publicKey, setPublicKey] = useState(rsa.publicKey)
  const [message, setMessage] = useState('')
  const [result, setResult] = useState('')
  const [limit, setLimit] = useState(null)
  const [validKey, setValidKey] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { if (rsa.publicKey) { setPublicKey(rsa.publicKey); setValidKey(false) } }, [rsa.publicKey])
  const validate = async () => { setError(''); setValidKey(false); try { const r = await api('/rsa/validate-public', { public_key: publicKey }); setPublicKey(r.public_key); setLimit(r.max_message_bytes); setValidKey(true) } catch (e) { setError(e.message) } }
  const encrypt = async () => {
    setError(''); setResult('')
    if (!message.length) return setError('Enter a short message to encrypt.')
    if (!validKey) return setError('Validate the public key before encrypting.')
    setBusy(true)
    try { const r = await api('/rsa/encrypt', { public_key: publicKey, plaintext: message }); setResult(r.ciphertext); setLimit(r.max_message_bytes) }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 02 / PUBLIC-KEY ENCRYPTION" title="RSA-OAEP Encryption" description="Encrypt a short text message with the recipient's public key and SHA-256 OAEP padding." icon={LockKeyhole} />
    <div className="workspace-grid rsa-workspace">
      <section className="panel"><div className="panel-title"><div><span className="eyebrow">RECIPIENT KEY</span><h2>Public key</h2></div><button className="text-button" onClick={validate}><Check size={14} /> Validate</button></div>
        <label className="field-label" htmlFor="rsa-pub">Public key · PEM</label><textarea id="rsa-pub" className="monospace" rows="8" value={publicKey} onChange={(e) => { setPublicKey(e.target.value); setValidKey(false); setLimit(null); setResult('') }} placeholder="Paste a public key or generate one in Key Generation…" />
        {validKey && <div className="inline-valid"><Check size={14} /> Valid RSA key · OAEP/SHA-256 limit {limit} UTF-8 bytes</div>}
        <label className="field-label" htmlFor="rsa-message">Plaintext message</label><textarea id="rsa-message" rows="4" value={message} onChange={(e) => { setMessage(e.target.value); setResult('') }} placeholder="Short message to encrypt…" />
        {validKey && <div className={`byte-counter ${new TextEncoder().encode(message).length > limit ? 'over' : ''}`}>{new TextEncoder().encode(message).length} / {limit} bytes · UTF-8</div>}
        <div className="button-row"><button className="button-primary" disabled={busy} onClick={encrypt}>{busy ? 'Encrypting…' : <><LockKeyhole size={16} /> Encrypt with RSA-OAEP</>}</button><button className="button-quiet" onClick={() => { setMessage(''); setResult(''); setError('') }}>Clear fields</button></div><Status type="error">{error}</Status>
      </section>
      <section className="panel result-panel"><div className="eyebrow">CIPHERTEXT OUTPUT</div><h2>Encrypted message</h2>{result ? <><OutputBox label="BASE64 CIPHERTEXT" value={result} /><div className="inline-valid"><ShieldCheck size={14} /> Encrypted with RSA-OAEP and SHA-256</div></> : <div className="empty-result"><span><LockKeyhole size={20} /></span><strong>Encrypted text appears here</strong><p>Validate a public key, enter a message, then encrypt.</p></div>}<div className="formula-card"><div className="eyebrow">MESSAGE SIZE LIMIT</div><p>OAEP with SHA-256 allows <code>k − 2(32) − 2</code> plaintext bytes, where <code>k</code> is the modulus size in bytes. RSA is for short messages; never silently truncate input.</p></div></section>
    </div>
  </div>
}

function RSADecryptPage() {
  const { rsa } = useContext(RSAContext)
  const [mode, setMode] = useState(rsa.keyId ? 'generated' : 'import')
  const [ciphertext, setCiphertext] = useState('')
  const [privateKey, setPrivateKey] = useState('')
  const [keyPassword, setKeyPassword] = useState('')
  const [validPrivate, setValidPrivate] = useState(false)
  const [recovered, setRecovered] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { if (rsa.keyId) setMode('generated') }, [rsa.keyId])
  const reset = () => { setCiphertext(''); setPrivateKey(''); setKeyPassword(''); setValidPrivate(false); setRecovered(''); setError(''); setMode(rsa.keyId ? 'generated' : 'import') }
  const validatePrivate = async () => { setError(''); setValidPrivate(false); try { const r = await api('/rsa/validate-private', { private_key: privateKey, private_key_password: keyPassword }); setValidPrivate(true); return r } catch (e) { setError(e.message); return null } }
  const decrypt = async () => {
    setError(''); setRecovered('')
    if (!ciphertext.trim()) return setError('Paste the Base64 ciphertext to decrypt.')
    if (mode === 'generated' && !rsa.keyId) return setError('No generated key is available. Generate a pair or import a private key.')
    if (mode === 'import' && !validPrivate) { const valid = await validatePrivate(); if (!valid) return }
    setBusy(true)
    try { const body = { ciphertext, ...(mode === 'generated' ? { key_id: rsa.keyId } : { private_key: privateKey, private_key_password: keyPassword }) }; const r = await api('/rsa/decrypt', body); setRecovered(r.plaintext) }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 02 / PRIVATE-KEY DECRYPTION" title="RSA-OAEP Decryption" description="Recover the message with its matching private key. Decryption uses OAEP and SHA-256." icon={UnlockKeyhole} />
    <div className="workspace-grid">
      <section className="panel"><div className="eyebrow">DECRYPT INPUT</div><h2>Provide ciphertext and key</h2>
        <label className="field-label" htmlFor="rsa-ciphertext">Ciphertext · standard Base64</label><textarea id="rsa-ciphertext" className="monospace" rows="5" value={ciphertext} onChange={(e) => { setCiphertext(e.target.value); setRecovered('') }} placeholder="Paste the complete ciphertext…" />
        <div className="mode-switch"><button className={mode === 'generated' ? 'mode-option active' : 'mode-option'} disabled={!rsa.keyId} onClick={() => { setMode('generated'); setValidPrivate(false); setError('') }}>Use generated key</button><button className={mode === 'import' ? 'mode-option active' : 'mode-option'} onClick={() => { setMode('import'); setError('') }}>Import private key</button></div>
        {mode === 'generated' ? <div className={rsa.keyId ? 'key-session-ready' : 'key-session-empty'}>{rsa.keyId ? <><ShieldCheck size={16} /><span>Matching {rsa.bits}-bit private key is loaded in this browser session.</span></> : <><KeyRound size={16} /><span>Generate a key pair first, or switch to import.</span></>}</div> : <><label className="field-label" htmlFor="rsa-private">Private key · PEM</label><textarea id="rsa-private" className="monospace" rows="7" value={privateKey} onChange={(e) => { setPrivateKey(e.target.value); setValidPrivate(false); setRecovered('') }} placeholder="Paste the matching private key…" /><label className="field-label" htmlFor="rsa-key-password">Private-key password if encrypted</label><input id="rsa-key-password" type="password" value={keyPassword} onChange={(e) => { setKeyPassword(e.target.value); setValidPrivate(false) }} placeholder="Leave empty for an unencrypted key" />{validPrivate && <div className="inline-valid"><Check size={14} /> Private key validated</div>}</>}
        <div className="button-row"><button className="button-primary" disabled={busy} onClick={decrypt}>{busy ? 'Decrypting…' : <><UnlockKeyhole size={16} /> Decrypt with RSA-OAEP</>}</button><button className="button-quiet" onClick={reset}>Clear fields</button></div><Status type="error">{error}</Status>
      </section>
      <section className="panel result-panel"><div className="eyebrow">RECOVERED PLAINTEXT</div><h2>Decrypted message</h2>{recovered !== '' ? <OutputBox label="PLAINTEXT" value={recovered} /> : <div className="empty-result"><span><UnlockKeyhole size={20} /></span><strong>Your recovered text appears here</strong><p>Only successful authenticated decryption displays an output.</p></div>}<div className="note-panel compact-note"><ShieldCheck size={17} /><p>The private key is used only for this request. Imported key text is not saved to project files.</p></div></section>
    </div>
  </div>
}

function RSADemoPage() {
  const values = { p: 3, q: 11, n: 33, phi: 20, e: 3, d: 7, m: 4, c: 31, recovered: 4 }
  return <div className="page-content">
    <PageHeader eyebrow="TASK 02 / NUMBER THEORY" title="RSA Numerical Example" description="A small worked example to trace modular arithmetic by hand." icon={Fingerprint} />
    <div className="warning-strip prominent"><span className="warning-mark">!</span><span><strong>Educational example only.</strong> These tiny values are completely insecure and are not used by real RSA-OAEP tools.</span></div>
    <div className="demo-flow">
      <section className="demo-step"><div className="step-number">01</div><div><span className="eyebrow">CHOOSE THE PRIME NUMBERS</span><h2>Start with two small primes</h2><p>For this hand calculation, choose <code>p = {values.p}</code> and <code>q = {values.q}</code>.</p></div><div className="math-chip">p = 3 <span>·</span> q = 11</div></section>
      <section className="demo-step"><div className="step-number">02</div><div><span className="eyebrow">COMPUTE MODULUS AND TOTIENT</span><h2>Build the key values</h2><p>The modulus is the product; Euler's totient counts the values coprime to it.</p></div><div className="math-stack"><code>n = p × q = 3 × 11 = 33</code><code>φ(n) = (p − 1)(q − 1) = 2 × 10 = 20</code></div></section>
      <section className="demo-step"><div className="step-number">03</div><div><span className="eyebrow">CHECK THE EXPONENTS</span><h2>Choose e and its inverse d</h2><p>The public exponent must be coprime with φ(n). The private exponent reverses it modulo φ(n).</p></div><div className="math-stack"><code>gcd(e, φ(n)) = gcd(3, 20) = 1</code><code>(e × d) mod φ(n) = (3 × 7) mod 20 = 1</code></div></section>
      <section className="demo-step"><div className="step-number">04</div><div><span className="eyebrow">ENCRYPT MESSAGE NUMBER M = 4</span><h2>Raise the message to the public exponent</h2><p>Reduce the result modulo n to obtain the ciphertext number.</p></div><div className="math-chip">C = M<sup>e</sup> mod n = 4<sup>3</sup> mod 33 = <strong>31</strong></div></section>
      <section className="demo-step"><div className="step-number">05</div><div><span className="eyebrow">DECRYPT C = 31</span><h2>Recover the original number</h2><p>Apply the private exponent and reduce modulo the same n.</p></div><div className="math-stack"><code>M = C<sup>d</sup> mod n = 31<sup>7</sup> mod 33</code><code>31 ≡ −2 (mod 33), so (−2)<sup>7</sup> = −128 ≡ 4 (mod 33)</code><div className="inline-valid"><Check size={15} /> Recovered M = 4, matching the original</div></div></section>
    </div>
  </div>
}

function LearningPage() {
  return <div className="page-content"><PageHeader eyebrow="REFERENCE / CONCEPTS" title="How the algorithms work" description="A short guide to the cryptographic ideas used throughout this toolkit." icon={BookOpen} />
    <div className="learning-grid"><article className="panel learning-card"><div className="eyebrow">01 · CLASSICAL</div><h2>Caesar Cipher</h2><p>A monoalphabetic substitution shifts each English letter by the same key. For a shift of 3, A becomes D and X wraps to A.</p><div className="formula-line">E(x) = (x + k) mod 26</div><div className="formula-line">D(x) = (x − k) mod 26</div><p className="muted">Only 26 shifts exist, so it offers no meaningful security.</p></article>
      <article className="panel learning-card"><div className="eyebrow">02 · SYMMETRIC</div><h2>AES-128-GCM</h2><p>AES uses the same secret key to encrypt and decrypt. GCM also produces an authentication tag that detects wrong passphrases or altered data.</p><div className="formula-line">Passphrase → PBKDF2-HMAC-SHA-256 → 128-bit key</div><p className="muted">A fresh salt and unique random nonce are stored with each ciphertext payload.</p></article>
      <article className="panel learning-card"><div className="eyebrow">03 · ASYMMETRIC</div><h2>RSA-OAEP</h2><p>The public key can be shared for encryption; the matching private key decrypts. OAEP adds randomized padding, and SHA-256 is used as its hash.</p><div className="formula-line">Maximum bytes = k − 2 × hLen − 2</div><p className="muted">RSA is for short messages. Larger systems usually combine public-key and symmetric encryption.</p></article></div>
    <div className="note-panel"><ShieldCheck size={18} /><p>This toolkit demonstrates common techniques using PyCryptodome. It is intended for education, not as a production key-management system.</p></div>
  </div>
}

function ComparisonPage() {
  const rows = [
    ['Type', 'Classical substitution', 'Symmetric authenticated encryption', 'Asymmetric public-key encryption'],
    ['Key material', 'Integer shift, 0–25', '128-bit key derived from passphrase', 'RSA public and private key pair'],
    ['Who can decrypt?', 'Anyone who knows the shift', 'Anyone who knows the passphrase', 'Holder of the matching private key'],
    ['Message size', 'Any text', 'Any text supported by AES-GCM', 'Short messages only; OAEP has a size limit'],
    ['Integrity check', 'No', 'Yes, through the GCM tag', 'OAEP padding validation'],
    ['Security in practice', 'Insecure; learning only', 'Modern when keys and nonces are managed correctly', 'Modern padding for short-message demonstrations'],
    ['Toolkit output', 'Readable shifted characters', 'Versioned Base64-compatible payload', 'Base64 ciphertext'],
  ]
  return <div className="page-content"><PageHeader eyebrow="REFERENCE / SIDE BY SIDE" title="Algorithm Comparison" description="Compare the building blocks and trade-offs of the three working algorithms." icon={ArrowDownUp} />
    <div className="panel comparison-panel"><div className="table-scroll"><table><thead><tr><th>PROPERTY</th><th>CAESAR CIPHER</th><th>AES-128-GCM</th><th>RSA-OAEP · SHA-256</th></tr></thead><tbody>{rows.map((row) => <tr key={row[0]}>{row.map((cell, i) => i === 0 ? <th key={cell}>{cell}</th> : <td key={cell}>{cell}</td>)}</tr>)}</tbody></table></div></div>
    <div className="note-panel"><BookOpen size={18} /><p>The numerical RSA demonstration is separate from this comparison and uses tiny values only to teach modular arithmetic.</p></div>
  </div>
}

export default App
