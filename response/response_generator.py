"""
UtilPulse Command Centre — Response Generator (Groq Powered)
=============================================================
Generates natural-language answers combining operational intent,
SQL results, standards retrieved via RAG, and data provenance.
Enforces strict refusal when questions fall outside the water utility domain.
All in-scope responses are generated exclusively by the Groq LLM (openai/gpt-oss-120b).
"""

import os
import pandas as pd
from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_BACKUP_MODEL,
    PROMPTS_DIR,
)

OUT_OF_SCOPE_MESSAGE = (
    "This question is outside the operational scope of UtilPulse Command Centre. "
    "UtilPulse is specialized exclusively in municipal water utility telemetry, water quality compliance (IS 10500:2012), "
    "network pressure, flow rates, pipe asset health, and leak diagnostics across the 10 monitored Indian cities "
    "(Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Pune, Ahmedabad, Jaipur, Lucknow, and Kolkata)."
)


class ResponseGenerator:
    """Generates natural-language answers exclusively using the Groq LLM with domain boundaries."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

        prompt_path = os.path.join(PROMPTS_DIR, "system_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as fh:
                self.system_prompt = fh.read()
        else:
            self.system_prompt = ""

    def generate(self, user_question: str, intent: dict, query_results_df: pd.DataFrame, sql_query: str, rag_context: str, provenance: str) -> str:
        """Generates response exclusively using the Groq LLM.

        Enforces strict domain boundaries — refuses to answer non-water inquiries.
        """
        # Strict domain boundary guardrail
        if intent and (intent.get("intent_type") == "out_of_scope" or intent.get("is_domain_relevant") is False):
            return OUT_OF_SCOPE_MESSAGE

        if not self.client:
            return (
                "⚠️ **Groq API Key Required**\n\n"
                "All responses in UtilPulse are generated directly by the LLM. "
                "Please ensure `GROQ_API_KEY` is configured in your `.env` file."
            )

        try:
            results_str = (
                query_results_df.head(50).to_string(index=False)
                if (query_results_df is not None and not query_results_df.empty)
                else "No matching telemetry records found in the database for the given criteria."
            )

            prompt = f"""DOMAIN & STATUTORY STANDARDS CONTEXT (from RAG knowledge base):
{rag_context if rag_context else "No domain context retrieved."}

DATA PROVENANCE:
{provenance if provenance else "Full municipal water network dataset."}

SQL QUERY EXECUTED:
{sql_query if sql_query else "No SQL query needed for this question."}

ACTUAL QUERY RESULTS FROM DATABASE:
{results_str}

USER QUESTION:
{user_question}

INSTRUCTIONS FOR YOUR ANSWER:
- You are EXCLUSIVELY an assistant for municipal water utility operations, water quality, and telemetry in the 10 monitored Indian cities.
- If the question is outside the water utility domain or unrelated to the dataset, REFUSE to answer and return the out-of-scope notice.
- Directly answer the USER QUESTION using the ACTUAL QUERY RESULTS and DOMAIN CONTEXT.
- If the question is a Yes/No question (e.g. starting with "Is", "Are", "Does", "Do", "Can", "Has", "Have", "Was", "Were"):
  Begin directly with a clear "Yes" or "No" (or "Generally yes / conditionally"), followed by the factual justification and the exact numbers from the database.
- If the question asks for a specific value or lookup, state the answer directly in 1-2 concise paragraphs.
- If the question asks for a comparison or ranking, summarize the findings clearly.
- Do NOT generate unsolicited boilerplate sections like "Recommended Operational Actions", "Executive Audit Summary", or general bulleted templates unless the user explicitly asked for recommendations or a full report.
- Stay strictly relevant to what was asked.

YOUR DIRECT RESPONSE:"""

            for model_candidate in [LLM_MODEL, LLM_BACKUP_MODEL]:
                try:
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        model=model_candidate,
                        temperature=0.1,
                    )
                    ans = chat_completion.choices[0].message.content.strip()
                    if ans:
                        return ans
                except Exception:
                    continue

            return "The language model was unable to generate a response. Please verify connectivity."

        except Exception as e:
            return f"⚠️ **LLM Generation Error**: {str(e)}"
