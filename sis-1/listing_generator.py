import os
import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import google.generativeai as genai

# Setup logging for cost/token tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentVariant(BaseModel):
    title: str = Field(description="SEO-friendly title, max 60 characters", max_length=60)
    description: str = Field(description="Max 500 token description matching the requested tone")
    key_features: List[str] = Field(description="Bullet points of key features")
    confidence_score: float = Field(description="Confidence score of generation quality from 0.0 to 1.0")

class SingleLanguageOutput(BaseModel):
    luxury: ContentVariant
    practical: ContentVariant
    emotional: ContentVariant

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimates the API cost based on token counts."""
    # Approximate pricing for demonstration (e.g., Gemini 1.5 Flash or Pro)
    input_cost = (input_tokens / 1_000_000) * 0.35
    output_cost = (output_tokens / 1_000_000) * 1.05
    return input_cost + output_cost

class ListingGenerator:
    def __init__(self, api_key: str = None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model_name = "gemini-1.5-pro"  # Use Pro to emulate GPT-4 reasoning

    def _generate_tone_variant(self, prompt: str, schema: Any, tone: str, temperature: float, max_tokens: int = 500) -> dict:
        """Helper to generate a specific tone variant with strict temperature and token limits."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=f"You are a real estate copywriter. Write in a {tone} tone.",
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        # Log Tokens and Cost Trackings
        usage = response.usage_metadata
        cost = estimate_cost(usage.prompt_token_count, usage.candidates_token_count)
        logger.info(f"[{tone.upper()}] Tokens - In: {usage.prompt_token_count}, Out: {usage.candidates_token_count} | Cost: ${cost:.6f}")
        
        return json.loads(response.text)

    def generate_english_base(self, image_data: str, features: Dict[str, Any]) -> dict:
        """Step 1: Generate the English source text in 3 variants."""
        base_prompt = f"""
        Extracted Image Data: {image_data}
        User Features: {json.dumps(features)}
        
        Generate a real estate listing based on the provided details. 
        It must include an SEO title (max 60 chars) and bullet points.
        """
        
        logger.info("Generating English Variants...")
        
        # A: Professional/Luxury (Temp 0.3)
        luxury = self._generate_tone_variant(
            prompt=base_prompt, 
            schema=ContentVariant, 
            tone="Professional and Luxury (for wealthy buyers)", 
            temperature=0.3
        )
        
        # B: Practical/Detailed (Temp 0.5)
        practical = self._generate_tone_variant(
            prompt=base_prompt, 
            schema=ContentVariant, 
            tone="Practical and Detailed (for investors highlighting ROI and layout)", 
            temperature=0.5
        )
        
        # C: Emotional/Storytelling (Temp 0.8)
        emotional = self._generate_tone_variant(
            prompt=base_prompt, 
            schema=ContentVariant, 
            tone="Emotional and Storytelling (for Instagram, highly engaging)", 
            temperature=0.8
        )
        
        return {
            "luxury": luxury,
            "practical": practical,
            "emotional": emotional
        }

    def _translate_and_verify(self, text_payload: dict, target_lang: str) -> dict:
        """Step 2: Translate using LLM and apply post-processing for real estate terminology accuracy."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=f"You are a professional real estate translator specialized in {target_lang} terminology."
        )
        
        prompt = f"""
        Translate the following English real estate listing variants into {target_lang}.
        Ensure that formal real estate terms (e.g., 'ensuite', 'ROI', 'sqm') are translated accurately according to local market norms in Almaty.
        
        Payload: {json.dumps(text_payload)}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=SingleLanguageOutput,
                temperature=0.3 # Keep translations strict and accurate
            )
        )
        
        # Log Tokens for Translation
        usage = response.usage_metadata
        cost = estimate_cost(usage.prompt_token_count, usage.candidates_token_count)
        logger.info(f"[TRANSLATE -> {target_lang}] Tokens - In: {usage.prompt_token_count}, Out: {usage.candidates_token_count} | Cost: ${cost:.6f}")
        
        translated_data = json.loads(response.text)
        
        # Post-Processing Step
        translated_data = self._post_process_terminology(translated_data, target_lang)
        
        return translated_data
        
    def _post_process_terminology(self, data: dict, lang: str) -> dict:
        """Step 3: Post-processing to enforce correct local real estate jargon."""
        # Simple programmatic checks representing the post-processing pipeline
        forbidden_words = {
            "Russian": {"арендная плата": "арендная ставка"}, # Example adjustments
            "Kazakh": {"үй": "пәтер"} # Example Context Fixes
        }
        
        if lang in forbidden_words:
            replacements = forbidden_words[lang]
            data_str = json.dumps(data, ensure_ascii=False)
            for bad_word, good_word in replacements.items():
                data_str = data_str.replace(bad_word, good_word)
            data = json.loads(data_str)
            
        return data

    def generate_all_listings(self, image_data: str, features: dict) -> dict:
        """Main orchestrator method."""
        # 1. Generate English
        english_variants = self.generate_english_base(image_data, features)
        
        # 2. Translate to Russian
        russian_variants = self._translate_and_verify(english_variants, "Russian")
        
        # 3. Translate to Kazakh
        kazakh_variants = self._translate_and_verify(english_variants, "Kazakh")
        
        return {
            "English": english_variants,
            "Russian": russian_variants,
            "Kazakh": kazakh_variants
        }

# Example usage (for local testing):
if __name__ == "__main__":
    generator = ListingGenerator(api_key=os.environ.get("GEMINI_API_KEY"))
    sample_features = {
        "price": "850,000 KZT",
        "rooms": "3",
        "location": "Medeu District, Almaty"
    }
    # generator.generate_all_listings("floor_plan_identified_as_120sqm.jpg", sample_features)
