from .translator import TranslatorAgent
from .quick_response import QuickResponseAgent
from .sentiment import SentimentAgent
from .lead_qualifier import LeadQualifierAgent
from .memory import MemoryAgent


class AgentOrchestrator:
    """Orchestrator that coordinates all 5 agents for message processing."""

    def __init__(self):
        self.translator = TranslatorAgent()
        self.responder = QuickResponseAgent()
        self.sentiment = SentimentAgent()
        self.qualifier = LeadQualifierAgent()
        self.memory = MemoryAgent()

    def process_message(self, message: str, client_id: str, save_to_memory: bool = True) -> dict:
        """
        Process an incoming message through all agents.

        Returns a comprehensive analysis with suggested responses.
        """
        # 1. Get client context from memory
        context = self.memory.get_context(client_id)

        # 2. Detect language and translate if needed
        translation = self.translator.translate(message)
        detected_language = translation["source_language"]
        translated_message = translation["translated"]

        # 3. Analyze sentiment and priority
        sentiment_analysis = self.sentiment.analyze(translated_message)

        # 4. Get conversation history for lead qualification
        history = context.get("recent_history", [])
        history.append({"role": "client", "content": translated_message})

        # 5. Score the lead
        lead_score = self.qualifier.score_lead(history)

        # 6. Generate response suggestions
        context_summary = context.get("summary", "")
        suggestions = self.responder.suggest_replies(
            translated_message,
            context=context_summary,
            count=3
        )

        # 7. Detect buying signals
        buying_signals = self.qualifier.detect_buying_signals(translated_message)

        # 8. Save to memory if enabled
        if save_to_memory:
            self.memory.save_message(client_id, "client", message)
            self.memory.save_client(client_id, language=detected_language)
            self.memory.update_lead_score(client_id, lead_score.get("score", "warm"))

        # Compile result
        result = {
            "client_id": client_id,
            "original_message": message,
            "translated_message": translated_message,
            "detected_language": detected_language,
            "sentiment": sentiment_analysis,
            "lead_qualification": lead_score,
            "buying_signals": buying_signals,
            "client_context": context,
            "suggested_responses": suggestions,
            "requires_immediate_attention": sentiment_analysis.get("requires_immediate_attention", False),
            "recommended_action": self._get_recommended_action(sentiment_analysis, lead_score, buying_signals),
        }

        return result

    def _get_recommended_action(self, sentiment: dict, lead: dict, signals: dict) -> str:
        """Determine the best recommended action based on all analyses."""
        if sentiment.get("requires_immediate_attention"):
            return "URGENT: Respond immediately - customer needs attention"

        if signals.get("signal_strength") == "strong":
            return "HOT LEAD: Strong buying signal detected - prioritize closing"

        if lead.get("score") == "hot":
            return "Ready to buy - present offer and close"

        if sentiment.get("category") == "complaint":
            return "Address complaint promptly - risk of losing customer"

        if lead.get("score") == "warm":
            return "Nurture lead - provide value and build relationship"

        if sentiment.get("category") == "sales_opportunity":
            return "Sales opportunity - qualify further and present value"

        return "Respond helpfully - standard inquiry"

    def prepare_response(self, response: str, client_id: str, tone: str = "professional") -> dict:
        """
        Prepare your response to be sent to the client.

        Adjusts tone and translates to client's language.
        """
        # Get client's language
        context = self.memory.get_context(client_id)
        client_language = context.get("client", {}).get("language", "en")

        # Adjust tone
        adjusted = self.translator.adjust_tone(response, tone=tone)

        # Translate to client's language
        translated = self.translator.translate_for_client(adjusted, client_language)

        # Save to memory
        self.memory.save_message(client_id, "assistant", response)

        return {
            "original": response,
            "adjusted_tone": adjusted,
            "translated": translated,
            "client_language": client_language,
            "ready_to_send": translated,
        }

    def get_inbox_overview(self, messages: list) -> dict:
        """
        Get an overview of multiple messages for inbox prioritization.

        messages: list of {"id": str, "client_id": str, "content": str}
        """
        analyzed = []

        for msg in messages:
            analysis = self.process_message(
                msg["content"],
                msg["client_id"],
                save_to_memory=False
            )
            analysis["message_id"] = msg.get("id")
            analyzed.append(analysis)

        # Sort by priority and urgency
        analyzed.sort(
            key=lambda x: (
                x.get("requires_immediate_attention", False),
                x.get("sentiment", {}).get("priority", 0),
                x.get("lead_qualification", {}).get("intent_level", 0),
            ),
            reverse=True
        )

        # Generate summary
        summary = {
            "total_messages": len(analyzed),
            "urgent": len([m for m in analyzed if m.get("requires_immediate_attention")]),
            "hot_leads": len([m for m in analyzed if m.get("lead_qualification", {}).get("score") == "hot"]),
            "complaints": len([m for m in analyzed if m.get("sentiment", {}).get("category") == "complaint"]),
            "prioritized_inbox": analyzed,
        }

        return summary

    def quick_analyze(self, message: str) -> dict:
        """Quick analysis without full processing - for speed."""
        sentiment = self.sentiment.get_sentiment(message)
        priority = self.sentiment.get_priority(message)
        category = self.sentiment.categorize(message)

        return {
            "sentiment": sentiment,
            "priority": priority,
            "category": category,
            "needs_attention": priority >= 8 or sentiment in ["angry", "frustrated"],
        }

    def learn_from_response(self, message: str, chosen_response: str):
        """Learn from a response you chose to improve future suggestions."""
        self.responder.learn_response(message, chosen_response)

    def get_qualification_questions(self, client_id: str) -> list:
        """Get smart qualification questions for a specific client."""
        history = self.memory.get_history(client_id)
        conversation = [{"role": msg["role"], "content": msg["content"]} for msg in history]

        missing = self.qualifier.get_missing_qualification_info(conversation)
        return self.qualifier.get_qualification_questions(missing_info=missing)

    def auto_reply(self, message: str, client_id: str, tone: str = "friendly", business_info: dict = None) -> dict:
        """
        Automatically generate the best reply for a message.

        Returns a ready-to-send response in the client's language.
        """
        # Process the message through all agents
        analysis = self.process_message(message, client_id)

        # Build context for generating the best response
        client_lang = analysis["detected_language"]
        sentiment = analysis["sentiment"]
        lead_score = analysis["lead_qualification"]
        context = analysis["client_context"]

        # Determine the best tone based on sentiment
        if sentiment.get("sentiment") in ["angry", "frustrated"]:
            tone = "professional"  # Be calm and professional with upset customers
        elif lead_score.get("score") == "hot":
            tone = "persuasive"  # Be persuasive with hot leads

        # Generate the best response using AI
        best_response = self.responder.generate_best_reply(
            message=analysis["translated_message"],
            sentiment=sentiment,
            lead_score=lead_score,
            context_summary=context.get("summary", ""),
            business_info=business_info or {}
        )

        # Translate back to client's language if needed
        if client_lang != "en":
            final_response = self.translator.translate_for_client(best_response, client_lang)
        else:
            final_response = best_response

        # Adjust tone
        final_response = self.translator.adjust_tone(final_response, tone=tone)

        # Save to memory
        self.memory.save_message(client_id, "assistant", final_response)

        return {
            "client_id": client_id,
            "original_message": message,
            "detected_language": client_lang,
            "sentiment": sentiment.get("sentiment"),
            "priority": sentiment.get("priority"),
            "lead_score": lead_score.get("score"),
            "auto_reply": final_response,
            "analysis": analysis,
        }
