const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Provide fetch for older Node versions
if (typeof fetch === 'undefined') {
  try {
    global.fetch = require('node-fetch');
  } catch (e) {
    console.warn('node-fetch not installed. Run: npm install node-fetch@2');
  }
}

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_API_KEY) {
  console.warn('Warning: OPENAI_API_KEY not set. Set it in .env or environment variables.');
}

app.post('/api/chat', async (req, res) => {
  try {
    const { messages, userText, model = 'gpt-4o-mini', temperature = 0.2, max_tokens = 600 } = req.body;

    const payload = messages && Array.isArray(messages)
      ? { model, messages, temperature, max_tokens }
      : {
          model,
          messages: [
            {
              role: 'system',
              content:
                "You are a helpful assistant focused on women's safety, helplines, reporting guidance, and self-defense tips. Provide clear, concise, safe guidance and when necessary advise contacting local authorities or helplines."
            },
            { role: 'user', content: userText || '' }
          ],
          temperature,
          max_tokens
        };

    const resp = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      const text = await resp.text();
      return res.status(resp.status).json({ error: text });
    }

    const data = await resp.json();
    const reply = (data.choices && data.choices[0] && (data.choices[0].message?.content || data.choices[0].text)) || '';
    return res.json({ reply, raw: data });
  } catch (err) {
    console.error('Proxy error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Proxy listening at http://localhost:${port}/api/chat`));