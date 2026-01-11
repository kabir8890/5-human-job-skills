from groq import Groq
import json
from config import GROQ_API_KEY
from business_config import PRICING, FAQ, BUSINESS_INFO, get_full_context


class QuickResponseAgent:
    """Quick Response Agent - Generates contextual reply suggestions."""

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.templates = {
            "pricing": [
                "Thanks for your interest! Our pricing starts at {price}. Would you like more details?",
                "Great question! I'd be happy to share our pricing. What specific product/service are you interested in?",
                "Our {product} is priced at {price}. This includes {features}. Interested?",
            ],
            "availability": [
                "Yes, that's currently available! Would you like to place an order?",
                "Let me check availability for you. What quantity are you looking for?",
                "That item is in stock and ready to ship. Shall I reserve one for you?",
            ],
            "shipping": [
                "We offer shipping to {location}. Delivery typically takes {time}.",
                "Shipping costs depend on your location. Where should we deliver?",
                "We ship worldwide! Standard delivery is {time}, express is {express_time}.",
            ],
            "hours": [
                "We're available {hours}. How can I help you today?",
                "Our business hours are {hours}. Feel free to reach out anytime!",
                "We're here {hours}. What can I assist you with?",
            ],
            "greeting": [
                "Hi there! Thanks for reaching out. How can I help you today?",
                "Hello! Great to hear from you. What can I do for you?",
                "Hey! Welcome! Let me know how I can assist you.",
            ],
            "thanks": [
                "You're welcome! Let me know if you need anything else.",
                "Happy to help! Don't hesitate to reach out anytime.",
                "My pleasure! Is there anything else I can help with?",
            ],
        }
        self.learned_responses = []

    def suggest_replies(self, message: str, context: str = "", count: int = 3) -> list:
        """Generate contextual reply suggestions based on message content."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate {count} different reply suggestions for this Instagram DM.
Keep replies conversational, helpful, and business-appropriate.
Each reply should be 1-2 sentences max.

Customer message: {message}
{"Context: " + context if context else ""}

Output as JSON array of strings only, no other text.
Example: ["Reply 1", "Reply 2", "Reply 3"]""",
                }
            ],
        )

        try:
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions[:count]
        except:
            return [response.choices[0].message.content]

    def get_template(self, category: str) -> list:
        """Get pre-built templates for common inquiries."""
        return self.templates.get(category, [])

    def categorize_inquiry(self, message: str) -> str:
        """Determine what type of inquiry this is."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": f"""Categorize this customer message into ONE of these categories:
pricing, availability, shipping, hours, greeting, thanks, product_info, complaint, other

Message: {message}

Output only the category name, nothing else.""",
                }
            ],
        )

        return response.choices[0].message.content.strip().lower()

    def auto_suggest(self, message: str, context: str = "") -> dict:
        """Automatically categorize and suggest responses."""
        category = self.categorize_inquiry(message)
        templates = self.get_template(category)
        ai_suggestions = self.suggest_replies(message, context, count=3)

        return {
            "category": category,
            "templates": templates,
            "ai_suggestions": ai_suggestions,
        }

    def learn_response(self, message: str, chosen_response: str):
        """Store a response to learn communication style over time."""
        self.learned_responses.append({
            "inquiry": message,
            "response": chosen_response,
        })

    def get_personalized_suggestion(self, message: str) -> str:
        """Generate suggestion based on learned communication style."""
        if not self.learned_responses:
            return self.suggest_replies(message, count=1)[0]

        examples = self.learned_responses[-10:]  # Last 10 responses
        examples_text = "\n".join(
            [f"Q: {ex['inquiry']}\nA: {ex['response']}" for ex in examples]
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on these example responses showing my communication style:

{examples_text}

Generate a reply for this new message that matches my style:
{message}

Output only the suggested reply.""",
                }
            ],
        )

        return response.choices[0].message.content

    def generate_best_reply(self, message: str, sentiment: dict, lead_score: dict, context_summary: str = "", business_info: dict = None) -> str:
        """Generate the single best reply based on all context."""
        business_name = BUSINESS_INFO.get("name", "amilie")
        business_context = get_full_context()

        sentiment_type = sentiment.get("sentiment", "neutral")
        category = sentiment.get("category", "general_inquiry")
        lead_type = lead_score.get("score", "warm")

        # Build instruction based on context
        tone_instruction = ""
        if sentiment_type in ["angry", "frustrated"]:
            tone_instruction = "The customer is upset. Be apologetic, empathetic, and solution-focused. Acknowledge their frustration."
        elif sentiment_type == "positive":
            tone_instruction = "The customer is happy. Be warm and enthusiastic. Build on their positive energy."
        elif lead_type == "hot":
            tone_instruction = "This is a hot lead ready to buy. Be helpful and guide them toward purchase without being pushy."
        elif category == "sales_opportunity":
            tone_instruction = "This is a sales opportunity. Be helpful, highlight value, and gently guide toward a decision."
        else:
            tone_instruction = "Be friendly, helpful, and professional."

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful Instagram business assistant for {business_name}.
You help respond to customer DMs professionally and naturally.
Keep responses short (1-3 sentences), friendly, and actionable.

{business_context}

{tone_instruction}

IMPORTANT: When asked about pricing, delivery, revisions, or payment - use the EXACT information above."""
                },
                {
                    "role": "user",
                    "content": f"""Generate the best reply for this Instagram DM.

Customer message: {message}
Customer sentiment: {sentiment_type}
Message category: {category}
Lead score: {lead_type}
{"Previous context: " + context_summary if context_summary else ""}

IMPORTANT: Reply in ENGLISH. Write a natural, helpful response. Only output the reply message, nothing else."""
                }
            ],
        )

        return response.choices[0].message.content
