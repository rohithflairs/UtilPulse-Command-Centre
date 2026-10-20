"""
UtilPulse Command Centre — Intent Parser (Groq Powered with Domain Guardrails)
==============================================================================
Uses Groq API (openai/gpt-oss-120b) to parse user natural-language questions into
structured intent dictionaries for SQL generation, visualization, and RAG context.
Enforces strict domain scope checking to reject unrelated general knowledge/trivia.
"""

import json
import os
import re
from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_BACKUP_MODEL,
    LLM_TEMPERATURE,
    VALID_COLUMNS,
    CATEGORICAL_VALUES,
    PROMPTS_DIR,
)


class IntentParser:
    """Parses user questions into structured operational intents with strict domain guardrails."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

        prompt_path = os.path.join(PROMPTS_DIR, "intent_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as fh:
                self.intent_template = fh.read()
        else:
            self.intent_template = ""

    def is_domain_relevant(self, user_question: str, intent: dict = None) -> bool:
        """Determines if a question is strictly within the scope of water utility telemetry.
        Returns False for general trivia, foreign geography, unrelated chat, coding, etc.
        """
        if not user_question or not user_question.strip():
            return False

        # 1. If intent was classified as out of scope by LLM
        if intent is not None:
            if intent.get("is_domain_relevant") is False or intent.get("intent_type") == "out_of_scope":
                return False

        q_low = user_question.lower().strip()

        # 2. Obvious out-of-scope non-water indicators (foreign countries, capitals, sports, trivia)
        out_of_scope_cues = [
            "capital of", "president of", "prime minister of", "world cup",
            "olympics", "movie", "actor", "actress", "song", "lyrics", "recipe",
            "stock price", "cryptocurrency", "bitcoin", "football", "cricket match",
            "who won", "write a poem", "write code", "python code", "tell me a joke",
            "translate", "capital city", "population of china",
            "china", "united states", "usa", "europe", "russia", "japan", "brazil",
            "france", "germany", "canada", "australia", "uk", "london", "paris", "beijing", "tokyo"
        ]
        has_out_cue = any(cue in q_low for cue in out_of_scope_cues)

        # 3. Water domain terms
        water_terms = [
            "water", "hydro", "potable", "drinking", "supply", "distribution", "network",
            "pipe", "pipes", "pipeline", "piping", "leak", "leaks", "burst", "bursts",
            "flow", "pressure", "velocity", "head loss", "volume", "consumption", "demand",
            "inlet", "outlet", "pump", "pumping", "reservoir", "tank", "treatment",
            "quality", "ph", "turbidity", "chlorine", "tds", "hardness", "iron", "nitrate",
            "coliform", "bacteria", "conductivity", "temperature", "water age",
            "nrw", "non-revenue", "non revenue", "compliance", "compliant", "interruption",
            "hdpe", "cast iron", "pvc", "ductile iron", "asbestos",
            "is 10500", "is10500", "cpheeo", "who standard", "bis standard", "potability",
            "mcgm", "delhi jal board", "djb", "bwssb", "hmwssb", "cmwssb", "pmrda",
            "amc water", "phed", "jal nigam", "kmc water"
        ]
        has_water_term = any(term in q_low for term in water_terms)

        # 4. Monitored Indian cities
        monitored_cities = [
            "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
            "pune", "ahmedabad", "jaipur", "lucknow", "kolkata"
        ]
        has_monitored_city = any(c in q_low for c in monitored_cities)

        # 5. Metadata queries (dataset, nodes, sensors)
        meta_terms = ["dataset", "telemetry", "node", "nodes", "sensor", "sensors", "utilpulse", "overview kpi", "monitored"]
        has_meta_term = any(m in q_low for m in meta_terms)

        # Disqualify if it has an out-of-scope cue and NO water terms
        if has_out_cue and not has_water_term:
            return False

        # In-scope if explicit water or telemetry concepts
        if has_water_term or has_meta_term:
            return True

        # In-scope if mentions a monitored city without city-trivia cues
        if has_monitored_city:
            city_trivia_cues = ["mayor", "history of", "best food", "hotels in", "population of", "capital of", "governor", "tourist"]
            if any(c in q_low for c in city_trivia_cues):
                return False
            return True

        # Default to False for anything else
        return False

    def parse(self, user_question: str) -> dict:
        """Parses natural-language user query into an operational intent dictionary."""
        if not user_question:
            return self._fallback_intent("")

        # 1. Attempt Groq LLM parsing
        if self.client:
            prompt = (
                self.intent_template
                .replace("{schema_columns}", ", ".join(VALID_COLUMNS))
                .replace("{user_question}", user_question)
            )

            for model_candidate in [LLM_MODEL, LLM_BACKUP_MODEL]:
                try:
                    chat_resp = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a precise JSON-only extraction system for water utility telemetry with strict domain guardrails."},
                            {"role": "user", "content": prompt}
                        ],
                        model=model_candidate,
                        temperature=0.0,
                    )
                    raw_text = chat_resp.choices[0].message.content.strip()
                    match = re.search(r"\{[\s\S]*\}", raw_text)
                    if match:
                        parsed = json.loads(match.group())
                        return self._clean_intent(parsed, user_question)
                except Exception:
                    continue

        # 2. Heuristic fallback if API unavailable
        return self._heuristic_parse(user_question)

    def _clean_intent(self, intent: dict, user_question: str) -> dict:
        """Validates, standardizes, and applies domain boundaries to intent structure."""
        # Check domain relevance
        is_relevant = self.is_domain_relevant(user_question, intent)
        if not is_relevant:
            intent["is_domain_relevant"] = False
            intent["intent_type"] = "out_of_scope"
            intent["metrics"] = []
            intent["filters"] = {}
            intent["group_by"] = []
            intent["chart_type"] = "none"
            intent["needs_domain_context"] = False
            intent["_original_question"] = user_question
            return intent

        intent["is_domain_relevant"] = True
        intent.setdefault("intent_type", "kpi_query")
        intent.setdefault("metrics", [])
        intent.setdefault("filters", {})
        intent.setdefault("aggregation", "mean")
        intent.setdefault("group_by", [])
        intent.setdefault("sort_by", None)
        intent.setdefault("sort_order", "desc")
        intent.setdefault("limit", 15)

        # Default chart_type to "none" unless explicitly valid
        c_type = str(intent.get("chart_type", "none")).lower().strip()
        if c_type not in ["bar", "line", "scatter", "heatmap"]:
            c_type = "none"

        # Suppress charts for Yes/No questions unless explicitly requested
        if self._is_yes_no_question(user_question) and not self._explicitly_wants_chart(user_question):
            c_type = "none"
            intent["group_by"] = []

        intent["chart_type"] = c_type
        intent.setdefault("needs_domain_context", True)
        intent["_original_question"] = user_question
        return intent

    def _is_yes_no_question(self, q: str) -> bool:
        """Detects if a question is formulated as a Yes/No question."""
        q_clean = q.strip().lower()
        yes_no_starters = (
            "is ", "are ", "does ", "do ", "can ", "could ",
            "has ", "have ", "was ", "were ", "will ", "would ", "should "
        )
        return q_clean.startswith(yes_no_starters) or q_clean.endswith("?") and any(
            q_clean.startswith(s) for s in ["is", "are", "does", "has", "was"]
        )

    def _explicitly_wants_chart(self, q: str) -> bool:
        """Detects if the query explicitly requested visual plotting."""
        q_lower = q.lower()
        chart_keywords = ["chart", "plot", "graph", "trend", "visual", "visualize", "diagram", "curve"]
        return any(k in q_lower for k in chart_keywords)

    def _heuristic_parse(self, q: str) -> dict:
        """Domain-tailored heuristic extractor for utility operations."""
        q_lower = q.lower()

        # Check domain relevance
        if not self.is_domain_relevant(q):
            return {
                "is_domain_relevant": False,
                "intent_type": "out_of_scope",
                "metrics": [],
                "filters": {},
                "aggregation": "mean",
                "group_by": [],
                "sort_by": None,
                "sort_order": "desc",
                "limit": 15,
                "chart_type": "none",
                "needs_domain_context": False,
                "_original_question": q,
            }

        is_yes_no = self._is_yes_no_question(q)
        wants_chart = self._explicitly_wants_chart(q)

        default_chart = "none"
        if wants_chart:
            default_chart = "line" if "trend" in q_lower else "bar"

        intent = {
            "is_domain_relevant": True,
            "intent_type": "kpi_query",
            "metrics": [],
            "filters": {},
            "aggregation": "mean",
            "group_by": [],
            "sort_by": None,
            "sort_order": "desc",
            "limit": 15,
            "chart_type": default_chart,
            "needs_domain_context": True,
            "_original_question": q,
        }

        # Detect City Filter
        for city in CATEGORICAL_VALUES["city"]:
            if city.lower() in q_lower:
                intent["filters"]["city"] = city
                break

        # Detect Zone Filter
        for zone in CATEGORICAL_VALUES["zone_id"]:
            if zone.lower() in q_lower or zone.replace("_", " ").lower() in q_lower:
                intent["filters"]["zone_id"] = zone
                break

        # Detect Season Filter
        for season in CATEGORICAL_VALUES["season"]:
            if season.lower() in q_lower or season.replace("_", " ").lower() in q_lower:
                intent["filters"]["season"] = season
                break

        # Metric Classification
        if any(w in q_lower for w in ["pressure compliance", "pressure standard", "pressure"]):
            intent["metrics"] = ["pressure_compliance_flag"]
            intent["intent_type"] = "compliance_check"
            if not is_yes_no and any(w in q_lower for w in ["all cities", "compare", "rank", "across cities"]):
                intent["group_by"] = ["city"]
                intent["chart_type"] = "bar"

        elif any(w in q_lower for w in ["chlorine compliance", "chlorine standard", "chlorine"]):
            intent["metrics"] = ["chlorine_compliance_flag"]
            intent["intent_type"] = "compliance_check"
            if "month" in q_lower or "trend" in q_lower:
                intent["group_by"] = ["month_name"]
                intent["chart_type"] = "line"
            elif not is_yes_no and any(w in q_lower for w in ["all cities", "compare", "across cities"]):
                intent["group_by"] = ["city"]
                intent["chart_type"] = "bar"

        elif any(w in q_lower for w in ["non-revenue", "nrw", "water loss", "losses"]):
            intent["metrics"] = ["non_revenue_water_pct"]
            intent["intent_type"] = "comparison"
            if not is_yes_no and any(w in q_lower for w in ["all cities", "compare", "which city", "rank"]):
                intent["group_by"] = ["city"]
                intent["chart_type"] = "bar"
            elif "material" in q_lower:
                intent["group_by"] = ["pipe_material"]
                intent["chart_type"] = "bar"

        elif any(w in q_lower for w in ["supply hours", "continuity", "hours of supply"]):
            intent["metrics"] = ["supply_hours_per_day"]
            if "month" in q_lower or "trend" in q_lower:
                intent["group_by"] = ["month_name"]
                intent["chart_type"] = "line"
            elif not is_yes_no and any(w in q_lower for w in ["all cities", "compare"]):
                intent["group_by"] = ["city"]
                intent["chart_type"] = "bar"

        elif any(w in q_lower for w in ["leak", "burst"]):
            intent["metrics"] = ["leak_detection_events"]
            intent["aggregation"] = "sum"
            if "material" in q_lower:
                intent["group_by"] = ["pipe_material"]
                intent["chart_type"] = "bar" if wants_chart or "which" in q_lower else "none"

        elif any(w in q_lower for w in ["daily volume", "water volume", "volume", "consumption"]):
            intent["metrics"] = ["daily_volume_m3"]
            intent["aggregation"] = "mean"
            if not is_yes_no and any(w in q_lower for w in ["city", "which city", "compare"]):
                intent["group_by"] = ["city"]

        elif any(w in q_lower for w in ["standard", "guideline", "is 10500", "cpheeo", "who", "safe to drink", "potable"]):
            intent["intent_type"] = "general_knowledge"
            intent["chart_type"] = "none"

        if is_yes_no and not wants_chart:
            intent["chart_type"] = "none"
            intent["group_by"] = []

        return intent

    def _fallback_intent(self, q: str) -> dict:
        return self._heuristic_parse(q)
