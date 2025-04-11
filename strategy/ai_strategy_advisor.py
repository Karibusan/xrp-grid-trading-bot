from ai.llm_client import ask_llm
import logging

logger = logging.getLogger(__name__)

def evaluate_market(log_excerpt):
    prompt = f"""
Here is a log summary from a crypto trading bot:

{log_excerpt}

Based on this, what strategic suggestions would you recommend? Be concise.
"""
    try:
        advice = ask_llm(prompt)
        logger.info(f"🤖 AI Strategy Suggestion: {advice}")
        return advice
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return None