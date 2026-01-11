from groq import Groq
import json
from config import GROQ_API_KEY


class SentimentAgent:
    """Sentiment & Priority Agent - Analyzes messages for urgency and tone."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, message: str) -> dict:
        """Full sentiment and priority analysis of a message."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this Instagram DM and provide:
1. sentiment: one of [positive, neutral, negative, angry, frustrated]
2. priority: score from 1-10 (10 = most urgent)
3. category: one of [urgent, sales_opportunity, general_inquiry, spam, complaint, follow_up]
4. requires_immediate_attention: true/false
5. summary: one sentence summary of the message intent

Message: {message}

Output as JSON only, no other text.""",
                }
            ],
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {
                "sentiment": "neutral",
                "priority": 5,
                "category": "general_inquiry",
                "requires_immediate_attention": False,
                "summary": message[:100],
            }

    def get_sentiment(self, message: str) -> str:
        """Quick sentiment detection only."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": f"""What is the emotional tone of this message?
Reply with ONE word: positive, neutral, negative, angry, or frustrated

Message: {message}""",
                }
            ],
        )

        return response.choices[0].message.content.strip().lower()

    def get_priority(self, message: str) -> int:
        """Quick priority scoring only."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": f"""Rate the urgency of this message from 1-10.
1 = not urgent, 10 = extremely urgent
Reply with only a number.

Message: {message}""",
                }
            ],
        )

        try:
            return int(response.choices[0].message.content.strip())
        except:
            return 5

    def categorize(self, message: str) -> str:
        """Categorize message type."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=30,
            messages=[
                {
                    "role": "user",
                    "content": f"""Categorize this message as ONE of:
urgent, sales_opportunity, general_inquiry, spam, complaint, follow_up

Message: {message}

Reply with only the category.""",
                }
            ],
        )

        return response.choices[0].message.content.strip().lower()

    def is_urgent(self, message: str) -> bool:
        """Quick check if message requires immediate attention."""
        analysis = self.analyze(message)
        return (
            analysis.get("requires_immediate_attention", False)
            or analysis.get("priority", 0) >= 8
            or analysis.get("sentiment") in ["angry", "frustrated"]
            or analysis.get("category") == "urgent"
        )

    def batch_analyze(self, messages: list) -> list:
        """Analyze multiple messages and sort by priority."""
        results = []
        for msg in messages:
            analysis = self.analyze(msg["content"])
            analysis["message_id"] = msg.get("id")
            analysis["client_id"] = msg.get("client_id")
            analysis["content"] = msg["content"]
            results.append(analysis)

        # Sort by priority (highest first)
        results.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return results

    def get_inbox_summary(self, messages: list) -> dict:
        """Get summary statistics for inbox."""
        analyzed = self.batch_analyze(messages)

        summary = {
            "total": len(analyzed),
            "urgent": len([m for m in analyzed if m.get("category") == "urgent"]),
            "sales_opportunities": len([m for m in analyzed if m.get("category") == "sales_opportunity"]),
            "complaints": len([m for m in analyzed if m.get("category") == "complaint"]),
            "needs_attention": len([m for m in analyzed if m.get("requires_immediate_attention")]),
            "sentiment_breakdown": {},
            "top_priority": analyzed[:5] if analyzed else [],
        }

        for msg in analyzed:
            sentiment = msg.get("sentiment", "neutral")
            summary["sentiment_breakdown"][sentiment] = (
                summary["sentiment_breakdown"].get(sentiment, 0) + 1
            )

        return summary
