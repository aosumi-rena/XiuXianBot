document.getElementById('save-btn').addEventListener('click', async () => {
  try {
    const updated = editor.get();
    const params = new URLSearchParams(window.location.search);
    const lang   = params.get('lang') || 'en';
    const resp = await fetch(`/config?lang=${lang}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated)
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      if (data.full_restart) {
        alert('⚠️ ' + data.message + '\n' + 'Core restart required.' + '\n' + 'i.e. You need to restart `start.py`');
      } else if (data.adapter_restart) {
        alert('⚠️ ' + data.message + '\n' + 'Adapter restart required.' + '\n' + 'i.e. You only need to restart affect platform adapter(s)');
      } else {
        alert('✅ ' + data.message);
      }
    } else {
      alert('❌ ' + data.message);
    }
  } catch (e) {
    alert('Error: ' + e);
  }
});
