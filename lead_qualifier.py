from groq import Groq
import json
from config import GROQ_API_KEY


class LeadQualifierAgent:
    """Lead Qualification Agent - Identifies serious buyers and scores leads."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.qualification_questions = {
            "budget": [
                "What budget range are you working with for this?",
                "Do you have a specific budget in mind?",
                "What's your investment range for this project?",
            ],
            "timeline": [
                "When are you looking to make a decision?",
                "What's your timeline for this?",
                "How soon do you need this?",
            ],
            "requirements": [
                "What specific features are most important to you?",
                "Can you tell me more about what you're looking for?",
                "What problem are you trying to solve?",
            ],
            "authority": [
                "Are you the decision maker for this purchase?",
                "Who else is involved in making this decision?",
                "Will anyone else need to approve this?",
            ],
        }

    def score_lead(self, conversation: list) -> dict:
        """Score a lead based on conversation history."""
        conversation_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation]
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this conversation and qualify the lead.

Conversation:
{conversation_text}

Evaluate and provide:
1. score: "hot", "warm", or "cold"
2. confidence: percentage 0-100
3. intent_level: 1-10 (10 = ready to buy)
4. budget_indicated: true/false (and amount if mentioned)
5. timeline_indicated: true/false (and timeframe if mentioned)
6. decision_maker: true/false/unknown
7. pain_points: list of identified needs/problems
8. objections: list of concerns mentioned
9. next_best_action: recommended follow-up action
10. reasoning: brief explanation of the score

Output as JSON only.""",
                }
            ],
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "score": "warm",
                "confidence": 50,
                "intent_level": 5,
                "reasoning": "Unable to fully analyze conversation",
            }

    def categorize(self, lead_data: dict) -> str:
        """Categorize lead as hot, warm, or cold."""
        score = lead_data.get("score", "warm")
        intent = lead_data.get("intent_level", 5)

        if score == "hot" or intent >= 8:
            return "hot"
        elif score == "cold" or intent <= 3:
            return "cold"
        else:
            return "warm"

    def get_qualification_questions(self, context: str = "", missing_info: list = None) -> list:
        """Get relevant qualification questions based on context."""
        if missing_info:
            questions = []
            for info_type in missing_info:
                if info_type in self.qualification_questions:
                    questions.append(self.qualification_questions[info_type][0])
            return questions

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on this conversation context, suggest 2-3 qualifying questions
to better understand if this is a serious buyer.

Questions should feel natural and conversational, not interrogating.

Context: {context if context else "New conversation, no context yet"}

Output as JSON array of question strings only.""",
                }
            ],
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return [
                "What brings you to us today?",
                "What are you looking to achieve?",
            ]

    def detect_buying_signals(self, message: str) -> dict:
        """Detect buying signals in a message."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this message for buying signals.

Message: {message}

Identify:
1. has_buying_signal: true/false
2. signal_strength: weak/moderate/strong
3. signals_detected: list of specific buying indicators found
4. suggested_response_approach: how to respond to move toward conversion

Output as JSON only.""",
                }
            ],
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "has_buying_signal": False,
                "signal_strength": "weak",
                "signals_detected": [],
            }

    def is_serious_buyer(self, conversation: list) -> bool:
        """Quick check if lead appears to be a serious buyer."""
        result = self.score_lead(conversation)
        return result.get("score") == "hot" or result.get("intent_level", 0) >= 7

    def get_missing_qualification_info(self, conversation: list) -> list:
        """Identify what qualification info is still needed."""
        conversation_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation]
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=128,
            messages=[
                {
                    "role": "user",
                    "content": f"""What qualification information is MISSING from this conversation?

Conversation:
{conversation_text}

Check for: budget, timeline, requirements, authority (decision maker)

Output as JSON array of missing items only.
Example: ["budget", "timeline"]""",
                }
            ],
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return ["budget", "timeline", "requirements"]

    def suggest_closing_approach(self, lead_data: dict) -> str:
        """Suggest how to close based on lead qualification."""
        if lead_data.get("score") == "hot":
            return "Direct close - ask for the sale"
        elif lead_data.get("score") == "warm":
            return "Nurture - address objections and provide more value"
        else:
            return "Qualify further - determine if worth pursuing"
