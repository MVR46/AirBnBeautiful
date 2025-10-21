"""RAG Service for neighborhood Q&A using OpenAI."""

import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

# Global models
embed_model = None
neighborhood_embeddings = {}
madrid_general_embedding = None
madrid_general_chunks = []
client = None


def init_rag_service(embedding_model: SentenceTransformer, neighborhood_data: Dict):
    """Initialize RAG service with embeddings."""
    global embed_model, neighborhood_embeddings, client, madrid_general_embedding, madrid_general_chunks
    
    embed_model = embedding_model
    
    # Load .env file RIGHT HERE - override any existing env vars
    env_path = Path(__file__).parent / '.env'
    print(f"DEBUG: Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path, override=True)
    
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"DEBUG: Attempting to load API key...")
    print(f"DEBUG: .env file exists: {env_path.exists()}")
    print(f"DEBUG: API key found: {api_key is not None}")
    if api_key:
        print(f"DEBUG: API key starts with: {api_key[:15]}...")
    
    if not api_key or api_key == 'sk-your-key-here':
        print("WARNING: OPENAI_API_KEY not set or using placeholder value. RAG chat will not work.")
        print("Please add your real OpenAI API key to backend/.env file")
        return
    
    try:
        client = OpenAI(api_key=api_key)
        print(f"✓ OpenAI client initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}")
        return
    
    # Import Madrid general info
    from data_service import MADRID_GENERAL_INFO
    
    # Precompute Madrid general knowledge embeddings
    print("Precomputing Madrid general knowledge embeddings...")
    madrid_general_chunks = [
        f"Madrid overview: {MADRID_GENERAL_INFO['description']}",
        f"Getting around Madrid: {MADRID_GENERAL_INFO['getting_around']}",
        f"Madrid food culture: {MADRID_GENERAL_INFO['food_culture']}",
        f"Madrid weather: {MADRID_GENERAL_INFO['weather']}",
        f"Language in Madrid: {MADRID_GENERAL_INFO['language']}",
        f"Madrid culture and lifestyle: {MADRID_GENERAL_INFO['culture']}"
    ]
    madrid_general_embedding = embed_model.encode(madrid_general_chunks, normalize_embeddings=True)
    
    # Precompute neighborhood embeddings
    print("Precomputing neighborhood embeddings for RAG...")
    for neighborhood, data in neighborhood_data.items():
        # Combine all context into chunks
        chunks = [
            f"{neighborhood} overview: {data['description']}",
            f"{neighborhood} safety: {data['safety']}",
            f"{neighborhood} nightlife: {data['nightlife']}",
            f"{neighborhood} transport: {data['transport']}",
            f"{neighborhood} cafes and restaurants: {data['cafes_restaurants']}",
            f"{neighborhood} noise level: {data['noise_level']}"
        ]
        
        # Embed each chunk
        chunk_embeddings = embed_model.encode(chunks, normalize_embeddings=True)
        
        neighborhood_embeddings[neighborhood] = {
            'chunks': chunks,
            'embeddings': chunk_embeddings
        }
    
    print(f"Precomputed embeddings for {len(neighborhood_embeddings)} neighborhoods + Madrid general knowledge")


def retrieve_relevant_chunks(question: str, neighborhood: str, listing_context: Optional[str] = None, top_k: int = 3) -> List[str]:
    """Retrieve most relevant context chunks for a question."""
    # Embed question
    q_embedding = embed_model.encode([question], normalize_embeddings=True)[0]
    
    all_chunks = []
    all_scores = []
    
    # Add listing-specific context if provided
    if listing_context:
        all_chunks.append(listing_context)
        listing_embedding = embed_model.encode([listing_context], normalize_embeddings=True)[0]
        listing_score = float(listing_embedding @ q_embedding)
        all_scores.append(listing_score * 1.2)  # Boost listing context relevance
    
    # Get neighborhood-specific chunks
    if neighborhood in neighborhood_embeddings:
        chunk_data = neighborhood_embeddings[neighborhood]
        similarities = chunk_data['embeddings'] @ q_embedding
        
        for i, score in enumerate(similarities):
            all_chunks.append(chunk_data['chunks'][i])
            all_scores.append(float(score))
    
    # Get Madrid general knowledge chunks
    if madrid_general_embedding is not None:
        madrid_similarities = madrid_general_embedding @ q_embedding
        
        for i, score in enumerate(madrid_similarities):
            all_chunks.append(madrid_general_chunks[i])
            all_scores.append(float(score) * 0.9)  # Slightly lower priority than neighborhood-specific
    
    # If we have no chunks at all, return empty
    if not all_chunks:
        return []
    
    # Get top-k chunks by score
    top_indices = np.argsort(all_scores)[-top_k:][::-1]
    
    return [all_chunks[i] for i in top_indices]


def generate_response(question: str, context_chunks: List[str], neighborhood: str) -> str:
    """Generate response using OpenAI with retrieved context."""
    if not client:
        return "Chat service unavailable. Please add your OpenAI API key to the backend/.env file (replace 'sk-your-key-here' with your actual key) and restart the server."
    
    # Build context
    context = "\n\n".join(context_chunks)
    
    # Create prompt
    prompt = f"""You are a local Madrid expert helping Airbnb guests. Answer the question based on the provided context about {neighborhood}.

Context:
{context}

Question: {question}

Provide a helpful, honest 2-3 sentence answer. Be conversational and practical. If the context doesn't fully answer the question, say so briefly and provide what you know."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a knowledgeable local guide for Madrid neighborhoods, helping Airbnb guests make informed decisions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        error_msg = str(e)
        print(f"OpenAI API error details: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        
        # Check for common errors
        if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
            return "⚠️ Invalid OpenAI API key. Please check that you've added your real API key to backend/.env and restart the server."
        elif "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            return "⚠️ OpenAI API quota exceeded. Please check your OpenAI account billing and usage limits."
        elif "rate_limit" in error_msg.lower():
            return "⚠️ Rate limit exceeded. Please wait a moment and try again."
        else:
            # Return helpful error with full details for debugging
            return f"⚠️ AI service error: {error_msg[:200]}. Please check the backend logs for details."


def answer_neighborhood_question(question: str, neighborhood: str, listing_info: Optional[Dict] = None) -> str:
    """Main function to answer a question about a neighborhood."""
    # Build listing context if provided
    listing_context = None
    if listing_info:
        listing_context = f"This listing in {neighborhood}: {listing_info.get('name', 'Apartment')}. "
        listing_context += f"Accommodates {listing_info.get('accommodates', 'N/A')} guests, "
        listing_context += f"{listing_info.get('bedrooms', 'N/A')} bedrooms, "
        listing_context += f"{listing_info.get('beds', 'N/A')} beds. "
        listing_context += f"Price: €{listing_info.get('price', 'N/A')}/night. "
        
        if listing_info.get('description'):
            desc = str(listing_info['description'])[:200]
            listing_context += f"Description: {desc}..."
    
    # Retrieve relevant context
    chunks = retrieve_relevant_chunks(question, neighborhood, listing_context, top_k=4)
    
    if not chunks:
        # Generic fallback if no data at all
        return f"I have limited specific information about {neighborhood}, but I can help with general Madrid questions. What would you like to know?"
    
    # Generate response
    response = generate_response(question, chunks, neighborhood)
    
    return response

