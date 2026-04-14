let rasaUrl = localStorage.getItem('rasa_url') || 'http://localhost:5005';
let senderId = localStorage.getItem('rasa_sender_id');

if (!senderId) {
  senderId = 'user_' + crypto.randomUUID().slice(0, 8);
  localStorage.setItem('rasa_sender_id', senderId);
}

const webhookUrl = () => rasaUrl.replace(/\/$/, '') + '/webhooks/rest/webhook';

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');

function appendMessage(role, text) {
  document.getElementById('welcome').style.display = 'none';

  const row = document.createElement('div');
  row.className = 'msg-row ' + role;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  row.appendChild(bubble);
  messagesEl.appendChild(row);

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = '';
  appendMessage('user', text);

  try {
    const res = await fetch(webhookUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender: senderId, message: text })
    });

    const data = await res.json();

    if (!data.length) {
      appendMessage('bot', '(Sem resposta do sistema)');
    } else {
      data.forEach(msg => {
        if (msg.text) appendMessage('bot', msg.text);
      });
    }

  } catch {
    appendMessage('bot', 'Erro de conexão com servidor');
  }
}

function sendQuick(text) {
  inputEl.value = text;
  send();
}

function handleKey(e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    send();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}

function clearChat() {
  messagesEl.innerHTML = '';
  document.getElementById('welcome').style.display = 'block';
}

function openModal() {
  document.getElementById('modal').classList.add('open');
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

function saveConfig() {
  const val = document.getElementById('rasaUrlInput').value.trim();
  if (val) {
    rasaUrl = val;
    localStorage.setItem('rasa_url', rasaUrl);
    document.getElementById('endpointLabel').textContent = val;
  }
  closeModal();
}