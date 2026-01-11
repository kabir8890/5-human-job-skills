# Instagram Agent Skills

A collection of 5 AI-powered agent skills designed to streamline daily Instagram business communication.

---

## 1. Multilingual Translator Agent

**Purpose:** Break language barriers in client communication

### Features
- **Auto-Detection:** Automatically identifies the language of incoming messages
- **Bidirectional Translation:**
  - Translates client messages → your preferred language
  - Translates your responses → client's language
- **Natural Tone:** Maintains conversational, human-like translations (not robotic)
- **Tone Adjustment:** Adapts message style based on context:
  - `friendly` - Casual, warm communication
  - `professional` - Formal business tone
  - `persuasive` - Sales-oriented, compelling language

### Usage
```python
translator.translate(message, target_language="en")
translator.adjust_tone(message, tone="professional")
```

---

## 2. Quick Response Agent

**Purpose:** Speed up response times with smart suggestions

### Features
- **Contextual Suggestions:** Generates reply options based on message content
- **Common Inquiry Handling:**
  - Pricing questions
  - Product availability
  - Service information
  - Business hours
- **Template Library:** Pre-built responses you can customize before sending
- **Style Learning:** Adapts to your communication patterns over time

### Usage
```python
responder.suggest_replies(message, count=3)
responder.get_template(category="pricing")
responder.send_response(message_id, response)
```

---

## 3. Sentiment & Priority Agent

**Purpose:** Prioritize your inbox based on urgency and emotion

### Features
- **Sentiment Analysis:** Detects emotional tone of messages
  - Positive, Neutral, Negative, Angry, Frustrated
- **Urgency Detection:** Flags time-sensitive messages
- **Smart Categorization:**
  - `urgent` - Requires immediate attention
  - `sales_opportunity` - Potential conversion
  - `general_inquiry` - Standard questions
  - `spam` - Low-value/promotional content
- **Priority Scoring:** 1-10 scale for inbox sorting

### Usage
```python
analyzer.analyze(message)
# Returns: {sentiment: "frustrated", priority: 8, category: "urgent"}
```

---

## 4. Lead Qualification Agent

**Purpose:** Identify serious buyers and filter out time-wasters

### Features
- **Intent Detection:** Determines if client is serious or just browsing
- **Structured Qualification:** Asks smart questions about:
  - Budget range
  - Timeline/urgency
  - Specific requirements
  - Decision-making authority
- **Lead Scoring:**
  - `hot` - Ready to buy, high intent
  - `warm` - Interested, needs nurturing
  - `cold` - Low intent, unlikely to convert
- **Time Optimization:** Filters low-quality inquiries automatically

### Usage
```python
qualifier.score_lead(conversation)
qualifier.get_qualification_questions(context)
qualifier.categorize(lead_data)
```

---

## 5. Conversation Memory Agent

**Purpose:** Never forget a client detail again

### Features
- **Client Profiles:** Stores key information per client:
  - Preferences and interests
  - Past issues/complaints
  - Order history
  - Communication preferences
- **Context Retrieval:** Provides relevant history before you respond
  - "This client asked about X last week"
  - "Previous order: Product Y on [date]"
- **Cross-Platform Tracking:** Maintains history across conversations
- **Personalization Engine:** Enables tailored interactions based on history

### Usage
```python
memory.get_context(client_id)
memory.save_detail(client_id, key="preference", value="fast shipping")
memory.get_history(client_id, limit=10)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Instagram DM Inbox                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Processor                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Translator   │    │   Sentiment   │    │    Memory     │
│    Agent      │    │    Agent      │    │    Agent      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────┐                          ┌───────────────┐
│     Lead      │                          │    Quick      │
│  Qualifier    │                          │   Response    │
└───────────────┘                          └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response to Client                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

- **Language:** Python 3.10+
- **AI/ML:** OpenAI API / Anthropic Claude API
- **Storage:** SQLite (local) / PostgreSQL (production)
- **Platform:** Instagram Graph API / Instagram Basic Display API

---

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_api_key
INSTAGRAM_ACCESS_TOKEN=your_token
PREFERRED_LANGUAGE=en
```

---

## Quick Start

```python
from agents import AgentOrchestrator

# Initialize all agents
orchestrator = AgentOrchestrator()

# Process incoming message
result = orchestrator.process_message(
    message="Hola, cuánto cuesta el producto?",
    client_id="user_123"
)

# Result includes:
# - Translated message
# - Sentiment analysis
# - Priority score
# - Lead qualification
# - Client context
# - Suggested responses
```

---

*Created for STARHIVE Instagram Workflow*
