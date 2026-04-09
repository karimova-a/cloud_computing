import streamlit as st
import google.generativeai as genai
import os
import json
from pydantic import BaseModel, Field
from typing import List
from prompts import SYSTEM_PROMPT

# Pydantic schemas for Structured Output
class LanguageListing(BaseModel):
    title: str = Field(description="Catchy title for the property listing")
    description: str = Field(description="SEO-optimized, engaging description formatted with markdown")
    seo_keywords: List[str] = Field(description="List of 5 SEO keywords")

class ListingResponse(BaseModel):
    english: LanguageListing = Field(description="Listing in English")
    russian: LanguageListing = Field(description="Listing in Russian")
    kazakh: LanguageListing = Field(description="Listing in Kazakh")

# --- UI Setup ---
st.set_page_config(page_title="KazRE Invest - AI Listing Enricher", page_icon="🏢", layout="wide")

st.title("🏢 KazRE Invest: AI Listing Enricher")
st.markdown("Transform basic property details into multi-lingual, SEO-optimized listings in seconds.")

# --- Sidebar (Settings & D2C FinOps) ---
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key. It will be used for this session only.")
if not api_key:
    # Try to load from environment
    api_key = os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.header("📊 FinOps Dashboard (D2C)")
st.sidebar.caption("Monitor estimated LLM API usage for your session.")

if "total_listings_generated" not in st.session_state:
    st.session_state.total_listings_generated = 0

st.sidebar.metric(label="Listings Generated", value=st.session_state.total_listings_generated)
# Hardcode approximate costs for D2C demonstration
apx_cost_per_listing = 0.03
st.sidebar.metric(label="Est. Cost Saved vs Human ($5)", value=f"${st.session_state.total_listings_generated * (5.00 - apx_cost_per_listing):.2f}")
st.sidebar.metric(label="Est. AI API Cost", value=f"${st.session_state.total_listings_generated * apx_cost_per_listing:.4f}")


# --- Main Application Area (R2F Interface) ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Property Facts")
    raw_details = st.text_area(
        "Enter raw property details here:",
        height=200,
        placeholder="- 3 bedroom, 2 bathroom\n- Golden Square (Almaty city center)\n- 120 sq meters\n- Just renovated, new Italian kitchen\n- High floor, mountain views\n- 850,000 KZT/month",
        help="Type bullet points or messy text. The AI will do the heavy lifting."
    )
    
    generate_btn = st.button("✨ Generate Listings", type="primary", use_container_width=True)

with col2:
    st.subheader("💡 Tips for Agents")
    st.info("- Include **Location** (e.g., Medeu district, Samal-2) for better local context.\n- Add **Price** if you want it included.\n- Mention **Unique Selling Points** (e.g., parking space, pet-friendly)")

if generate_btn:
    if not api_key:
        st.error("⚠️ Please provide a Gemini API Key in the sidebar to proceed.")
    elif not raw_details.strip():
        st.warning("⚠️ Please enter some property details before generating.")
    else:
        with st.spinner("🤖 AI is writing and translating..."):
            try:
                # API Configuration
                genai.configure(api_key=api_key)
                
                # Dynamically find the best available model for your API key
                best_model = "gemini-pro"
                for m in genai.list_models():
                    if "generateContent" in m.supported_generation_methods:
                        name = m.name.replace("models/", "")
                        if "gemini-1.5" in name or "gemini-2." in name or "gemini-3." in name:
                            best_model = name
                            break
                
                model = genai.GenerativeModel(
                    model_name=best_model,
                    system_instruction=SYSTEM_PROMPT
                )
                
                # We enforce the JSON schema so we get reliable, parsable data
                response = model.generate_content(
                    f"Raw details from agent:\n{raw_details}",
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=ListingResponse,
                        temperature=0.7 # Slight creativity
                    )
                )
                
                # Parsing the response
                result = json.loads(response.text)
                
                # Update FinOps state
                st.session_state.total_listings_generated += 1
                
                st.success("🎉 Listings successfully generated!")
                
                # Display Results in Tabs
                tab_en, tab_ru, tab_kz = st.tabs(["🇬🇧 English", "🇷🇺 Русский", "🇰🇿 Қазақша"])
                
                with tab_en:
                    st.markdown(f"### {result['english']['title']}")
                    st.markdown(result['english']['description'])
                    st.caption(f"**SEO Keywords:** {', '.join(result['english']['seo_keywords'])}")
                    st.code(f"{result['english']['title']}\n\n{result['english']['description']}\n\nKeywords: {', '.join(result['english']['seo_keywords'])}", language="markdown")
                
                with tab_ru:
                    st.markdown(f"### {result['russian']['title']}")
                    st.markdown(result['russian']['description'])
                    st.caption(f"**SEO Keywords:** {', '.join(result['russian']['seo_keywords'])}")
                    st.code(f"{result['russian']['title']}\n\n{result['russian']['description']}\n\nKeywords: {', '.join(result['russian']['seo_keywords'])}", language="markdown")

                with tab_kz:
                    st.markdown(f"### {result['kazakh']['title']}")
                    st.markdown(result['kazakh']['description'])
                    st.caption(f"**SEO Keywords:** {', '.join(result['kazakh']['seo_keywords'])}")
                    st.code(f"{result['kazakh']['title']}\n\n{result['kazakh']['description']}\n\nKeywords: {', '.join(result['kazakh']['seo_keywords'])}", language="markdown")
                    
            except Exception as e:
                st.error(f"❌ An error occurred during API execution. Error details: {str(e)}")
