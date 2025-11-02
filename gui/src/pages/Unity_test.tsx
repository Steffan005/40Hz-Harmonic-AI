// MINIMAL TEST COMPONENT
export function Unity() {
  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontSize: '2rem',
      fontFamily: 'system-ui'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1>🌌 UNITY TEST 🌌</h1>
        <p>If you see this, React is rendering!</p>
        <p style={{ fontSize: '1rem', opacity: 0.8, marginTop: '2rem' }}>
          The city awaits awakening...
        </p>
      </div>
    </div>
  );
}
