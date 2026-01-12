# amilie - Instagram Auto-Replyer 

An AI-powered Instagram DM assistant that automatically generates smart replies for your business.

## Features

- **Multilingual Support** - Auto-detects language and replies in the same language
- **Smart Replies** - AI generates contextual, professional responses
- **Sentiment Analysis** - Detects customer mood (happy, angry, frustrated)
- **Lead Scoring** - Identifies hot/warm/cold leads
- **Pricing & FAQ** - Bot knows your exact prices and policies
- **Auto-Copy** - Replies automatically copy to clipboard
- **Conversation Logs** - All chats saved for reference
- **Client Memory** - Remembers past conversations with each client

## 5 AI Agents

| Agent | Purpose |
|-------|---------|
| Translator | Language detection & translation |
| Quick Response | Generates smart replies |
| Sentiment | Analyzes customer mood & urgency |
| Lead Qualifier | Scores leads (hot/warm/cold) |
| Memory | Stores client history |

## Installation

```bash
# Clone the repo
git clone https://github.com/kabir8890/amilie-instagram-bot.git
cd amilie-instagram-bot

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

## Usage

```bash
# Run demo
python main.py

# Auto-reply mode (recommended)
python main.py --auto

# Interactive mode (pick from suggestions)
python main.py --interactive
```

## Configuration

Edit `business_config.py` to set your:
- Pricing
- Delivery time
- Revision policy
- Payment methods

## Example

```
Customer: "How much for a logo?"

Bot Analysis:
  Language: English
  Sentiment: Neutral
  Lead Score: Warm

Auto-Reply: "Our logo designs start at $50-100 depending on
complexity. Would you like to see some examples?"
```

## Project Structure

```
amilie-instagram-bot/
├── agents/              # 5 AI agents
│   ├── translator.py
│   ├── quick_response.py
│   ├── sentiment.py
│   ├── lead_qualifier.py
│   └── memory.py
├── main.py              # Entry point
├── business_config.py   # Your pricing & FAQ
├── config.py            # API configuration
└── requirements.txt     # Dependencies
```

## Tech Stack

- Python 3.10+
- Groq API (Llama 3.3 70B)
- SQLite (client memory)

## License

MIT License

---

# Video link
https://youtu.be/FtMpcVDxxzw?si=6K-yDlNwhtD2dIgg

