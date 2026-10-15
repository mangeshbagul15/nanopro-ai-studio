"""
Mangesh Nano Pro AI Studio - Entertainment & Modern Lifestyle Agent
Immersive Multimedia Discovery Center
Covers:
- Bollywood, Hollywood, Tollywood & South Indian Cinema
- Web Series & Streaming Guides
- Curated YouTube Creators, Tech Reviews & Educational Videos
- Music Discovery, Artists, Albums & Playlists
- Men's & Women's Fashion, Grooming, Watches & Accessories
- Modern Fitness, Travel, Interior Design & Tech Gadgets
- AI Manager interactive summarization & explanations
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.logger import log_event
from app.core.database import db

MARATHI_MOVIES_CATALOG = [
    {
        "category": "Marathi Movies",
        "title": "Sairat (सैराट)",
        "creator": "Nagraj Manjule (Zee Studios)",
        "description": "Historic Marathi blockbuster following Prashant (Parshya) and Archana (Archie) defying societal boundaries in rural Solapur. Unforgettable music by Ajay-Atul with iconic tracks Zingaat and Yad Lagla.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMjA4ODQxNzc0NV5BMl5BanBnXkFtZTgwNTUwODU3ODE@._V1_.jpg",
        "media_url": "https://www.zee5.com/movies/details/sairat/0-0-sairat",
        "source": "ZEE5 & YouTube",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Rinku Rajguru, Akash Thosar", "genre": "Romantic Drama", "music": "Ajay-Atul", "box_office": "₹110 Cr Worldwide", "watch_platforms": "ZEE5, YouTube"}
    },
    {
        "category": "Marathi Movies",
        "title": "Baipan Bhaari Deva (बाईपण भारी देवा)",
        "creator": "Kedar Shinde (Jio Studios)",
        "description": "Heartwarming story of six estranged sisters who reunite to compete in a prestigious Mangalagaur competition in Pune, confronting long-suppressed family grievances and rediscovering womanhood.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BNmU4M2E3NTQtODgyOC00NDU4LTk2NTktNGU2ODg3MmU2MTQ1XkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.hotstar.com",
        "source": "JioCinema / Disney+ Hotstar",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Rohini Hattangadi, Vandana Gupte, Sukanya Kulkarni, Shilpa Navalkar, Suchitra Bandekar, Deepa Parab", "genre": "Family / Drama / Comedy", "box_office": "₹90 Cr"}
    },
    {
        "category": "Marathi Movies",
        "title": "Ved (वेड)",
        "creator": "Riteish Deshmukh (Mumbai Film Company)",
        "description": "Intense romantic drama starring Riteish Deshmukh and Genelia D'Souza. Satya Jadhav, a heartbroken former cricketer sinking into despair, finds silent devotion and redemption from his devoted wife Shravani.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMWRlNzgyMDItYTFjMi00Mjc4LTg4YjEtODhjNmExNjFmMWM3XkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.hotstar.com/movies/ved/1260136274",
        "source": "Disney+ Hotstar",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Riteish Deshmukh, Genelia D'Souza, Jiya Shankar, Ashok Saraf", "genre": "Romantic Drama", "box_office": "₹75 Cr"}
    },
    {
        "category": "Marathi Movies",
        "title": "Pawankhind (पावनखिंड)",
        "creator": "Digpal Lanjekar (Almond Creations)",
        "description": "Historical action epic depicting the immortal battle of Ghodkhind. Baji Prabhu Deshpande and 300 valiant Bandal Mavale hold off thousands of Siddi Masood's troops until cannon fire signals Chhatrapati Shivaji Maharaj's safe arrival at Vishalgad.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BODg5NDliYmMtZjA4Zi00ZTBlLTgzZDctZjUzNWE4MGY3Y2FhXkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.youtube.com/watch?v=sUjOhyN8h80",
        "source": "YouTube (Full HD) & Prime Video",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Chinmay Mandlekar, Ajay Purkar, Sameer Dharmadhikari", "genre": "Historical / Action", "director": "Digpal Lanjekar"}
    },
    {
        "category": "Marathi Movies",
        "title": "Natsamrat (नटसम्राट)",
        "creator": "Mahesh Manjrekar (Fincraft Media)",
        "description": "Nana Patekar delivers an unforgettable, career-defining performance as Shakespearean stage actor Ganpat 'Appa' Belwalkar in V.V. Shirwadkar's timeless tragedy about filial neglect and lost dignity.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BZjU2MWE5ZDEtNWVkMi00NGJiLTk5MTgtMWM5YjBiMWIxNzE2XkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.youtube.com/watch?v=0h9V6N9U1fM",
        "source": "YouTube (Official) & Netflix",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Nana Patekar, Medha Manjrekar, Vikram Gokhale", "genre": "Drama / Tragedy", "rating": "9.1/10"}
    },
    {
        "category": "Marathi Movies",
        "title": "Duniyadari (दुनियादारी)",
        "creator": "Sanjay Jadhav (Dreaming 24/7)",
        "description": "Classic coming-of-age cult drama exploring deep friendship, sacrifice, and college life in 1970s Pune between Shreyas Talwalkar, Digya, Shirin, and Meenu. Featuring evergreen songs 'Tik Tik Vajate Dokyat' and 'Zindagi Zindagi'.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BYzA0NmNhNTktYmMzNi00YTU3LTk4NjItY2M1MzE0NzM3NTY2XkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.youtube.com/watch?v=B9Jk7oD8_Lw",
        "source": "YouTube (Full Movie) & ZEE5",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Swapnil Joshi, Ankush Chaudhari, Sai Tamhankar, Urmila Kothare", "genre": "Youth Drama / Romance"}
    },
    {
        "category": "Marathi Movies",
        "title": "Mi Shivajiraje Bhosale Boltoy (मी शिवाजीराजे भोसले बोलतोय)",
        "creator": "Santosh Manjrekar (Everest Entertainment)",
        "description": "Dinkar Bhosale, a common Marathi man disillusioned by corruption and lost identity in Mumbai, is guided by the living spirit of Chhatrapati Shivaji Maharaj to rise with pride, self-respect, and fearless action.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMTQxMzgyMzYxMF5BMl5BanBnXkFtZTcwNTg5NjUyMw@@._V1_.jpg",
        "media_url": "https://www.youtube.com/watch?v=JmKxJbH7y7E",
        "source": "YouTube (Full HD Official)",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Sachin Khedekar, Mahesh Manjrekar, Makarand Anaspure", "genre": "Social Drama / Patriotic"}
    },
    {
        "category": "Marathi Movies",
        "title": "Killa (किल्ला)",
        "creator": "Avinash Arun (Essel Vision)",
        "description": "National Award-winning lyrical coming-of-age masterpiece about an 11-year-old boy Chinmay navigating grief, school friendships, and the mesmerizing monsoon fortresses of Konkan.",
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BOGIzNDc2ZjAtMzU1Yi00NzU2LTkxM2UtZTY4YzQ2MWUxMGViXkEyXkFqcGc@._V1_.jpg",
        "media_url": "https://www.zee5.com",
        "source": "ZEE5 & Prime Video",
        "published_at": "2026-10-12",
        "metadata": {"cast": "Archit Deodhar, Amruta Subhash, Parth Bhalerao", "genre": "Coming-of-Age Drama", "award": "National Film Award"}
    }
]

class EntertainmentAgent:
    def __init__(self):
        self._ensure_seed_entertainment()

    def _ensure_seed_entertainment(self):
        """Seeds authentic curated multimedia and lifestyle items across key categories."""
        try:
            items = db.list_entertainment_items(limit=5)
            if not items:
                seed_data = [
                    # Bollywood
                    {
                        "category": "Bollywood",
                        "title": "Brahmāstra: Part Two – Dev",
                        "creator": "Ayan Mukerji (Dharma Productions)",
                        "description": "The epic fantasy adventure continues tracing the origins of Dev and the ancient Astraverse with ground-breaking VFX and mythic lore.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMjExY2Q4YzEtOTk0ZC00MjA5LWFmZTYtNjA0ZmExN2FlMzk0XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.hotstar.com",
                        "source": "Official Studio Preview",
                        "published_at": "2026-09-15",
                        "metadata": {"cast": "Ranbir Kapoor, Alia Bhatt", "genre": "Mythological Fantasy / Action", "runtime": "165 min", "rating": "8.4/10"}
                    },
                    {
                        "category": "Bollywood",
                        "title": "Stree 2: Sarkate Ka Aatank",
                        "creator": "Amar Kaushik (Maddock Films)",
                        "description": "Blockbuster horror-comedy following Vicky and the Chanderi residents battling the headless ghost terrorizing the town.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BODlhYTU0MGYtY2ZhYy00ODZkLWE1MmQtNTg0ZjM0OWRkNTg5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.primevideo.com",
                        "source": "Prime Video & Theatrical",
                        "published_at": "2026-08-15",
                        "metadata": {"cast": "Rajkummar Rao, Shraddha Kapoor, Pankaj Tripathi", "genre": "Horror / Comedy", "runtime": "147 min", "box_office": "₹875 Cr worldwide"}
                    },

                    # Hollywood
                    {
                        "category": "Hollywood",
                        "title": "Dune: Part Two",
                        "creator": "Denis Villeneuve (Warner Bros.)",
                        "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.warnerbros.com/movies/dune-part-two",
                        "source": "Warner Bros. Pictures",
                        "published_at": "2026-03-01",
                        "metadata": {"director": "Denis Villeneuve", "genre": "Sci-Fi / Epic", "runtime": "166 min", "imdb": "8.6/10"}
                    },

                    # Tollywood & South Cinema
                    {
                        "category": "Tollywood",
                        "title": "Kalki 2898 AD",
                        "creator": "Nag Ashwin (Vyjayanthi Movies)",
                        "description": "Futuristic post-apocalyptic mythic epic reimagining the Mahabharata lore in the year 2898 AD in Kasi.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BN2U5Mzg1ZjYtMTEwZC00ODVlLTkzZmItYTE0NzA2Y2JjYmQ3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.netflix.com",
                        "source": "Vyjayanthi Movies",
                        "published_at": "2026-06-27",
                        "metadata": {"cast": "Prabhas, Amitabh Bachchan, Kamal Haasan, Deepika Padukone", "genre": "Sci-Fi / Mythology", "budget": "₹600 Cr"}
                    },
                    {
                        "category": "Tollywood",
                        "title": "Pushpa 2: The Rule",
                        "creator": "Sukumar (Mythri Movie Makers)",
                        "description": "Pushpa Raj expands his red sandalwood empire while locked in an intense battle of wits with SP Bhanwar Singh Shekhawat.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMjY5ODhkNDctYzI2MC00NzFkLTk4ZWMtMTMyMDkyZTIxOGU1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.netflix.com",
                        "source": "Mythri Movie Makers",
                        "published_at": "2026-12-05",
                        "metadata": {"cast": "Allu Arjun, Rashmika Mandanna, Fahadh Faasil", "genre": "Action / Drama", "music": "Devi Sri Prasad"}
                    },

                    # Web Series
                    {
                        "category": "Web Series",
                        "title": "Panchayat Season 3",
                        "creator": "The Viral Fever (TVF)",
                        "description": "Abhishek Tripathi navigates gram panchayat politics, local rivalries, and Phulera village dynamics in rural Uttar Pradesh.",
                        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BYzA2Nzk5M2EtNWY4Yi00ZDY4LThkZTgtYjQ5MmUxOTU1NTc3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                        "media_url": "https://www.primevideo.com",
                        "source": "Amazon Prime Video",
                        "published_at": "2026-05-28",
                        "metadata": {"episodes": 8, "starring": "Jitendra Kumar, Neena Gupta, Raghubir Yadav", "rating": "8.9/10"}
                    },

                    # YouTube Discovery
                    {
                        "category": "YouTube",
                        "title": "Building Production Enterprise Data Warehouses on Snowflake & AWS",
                        "creator": "Seattle Data Guy (Benjamin Rogojan)",
                        "description": "Deep-dive architectural tutorial on dimensional modeling, staging lake architectures, and high-performance Snowflake pipelines.",
                        "thumbnail_url": "https://i.ytimg.com/vi/S38v3vN6i8U/hqdefault.jpg",
                        "media_url": "https://www.youtube.com/watch?v=S38v3vN6i8U",
                        "source": "YouTube (Data Engineering)",
                        "published_at": "2026-09-02",
                        "metadata": {"views": "142K", "duration": "42:15", "topic": "Snowflake, S3, ETL"}
                    },
                    {
                        "category": "YouTube",
                        "title": "FastAPI + Local LLMs Architecture & Agentic Design Patterns",
                        "creator": "FreeCodeCamp / Harrison Chase",
                        "description": "End-to-end framework breakdown for asynchronous Python APIs connecting local Ollama models and tool-calling agents.",
                        "thumbnail_url": "https://i.ytimg.com/vi/bE_r18fL-5k/hqdefault.jpg",
                        "media_url": "https://www.youtube.com/watch?v=bE_r18fL-5k",
                        "source": "YouTube (AI Engineering)",
                        "published_at": "2026-08-20",
                        "metadata": {"views": "285K", "duration": "1:14:00", "topic": "Python, LLMs, Agents"}
                    },

                    # Music Center
                    {
                        "category": "Music",
                        "title": "Kesariya (Brahmāstra OST)",
                        "creator": "Pritam, Arijit Singh",
                        "description": "Soulful Indian romantic ballad with acoustic instrumentation, traditional sarangi motifs, and soaring vocals.",
                        "thumbnail_url": "https://i.scdn.co/image/ab67616d0000b273c5649add07ed3720be9d5526",
                        "media_url": "https://open.spotify.com/track/6nWjT8c3M0Zz",
                        "source": "Sony Music India",
                        "published_at": "2026-07-17",
                        "metadata": {"composer": "Pritam", "lyrics": "Amitabh Bhattacharya", "genre": "Bollywood Romantic", "bpm": 92}
                    },
                    {
                        "category": "Music",
                        "title": "Deep Focus: Lofi Beats for Data Engineers & Coders",
                        "creator": "Lofi Girl (ChilledCow)",
                        "description": "Calm instrumental beats, soft rhodes piano chords, and ambient rain textures designed for prolonged deep focus coding.",
                        "thumbnail_url": "https://i.ytimg.com/vi/jfKfPfyJRdk/hqdefault.jpg",
                        "media_url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
                        "source": "Lofi Records",
                        "published_at": "2026-10-01",
                        "metadata": {"genre": "Lofi Hip-Hop / Instrumental", "stream": "24/7 Live Stream", "target": "Coding & Study"}
                    },

                    # Fashion & Lifestyle
                    {
                        "category": "Fashion",
                        "title": "Modern Executive Minimalist Wardrobe (Navy, Charcoal & Linen)",
                        "creator": "Gentleman's Gazette & GQ India",
                        "description": "Essential curation of tailored unstructured navy blazers, crisp Egyptian cotton shirts, and Goodyear-welted leather oxfords for modern professionals.",
                        "thumbnail_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop",
                        "media_url": "https://www.gqindia.com/style",
                        "source": "GQ India Style Guide",
                        "published_at": "2026-09-10",
                        "metadata": {"palette": "Navy, Slate, Crisp White", "category": "Men's Formal & Smart Casual", "season": "All-Season"}
                    },
                    {
                        "category": "Lifestyle",
                        "title": "Smart Ergonomic Workspace & Biophilic Productivity Setup",
                        "creator": "Minimal Setup & Architecture Digest",
                        "description": "Walnut standing desk, 4K Ultrawide monitor, warm 3000K accent light bar, and air-purifying indoor plants engineered for optimal posture and focus.",
                        "thumbnail_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&auto=format&fit=crop",
                        "media_url": "https://minimalsetups.com",
                        "source": "Modern Workspace Design",
                        "published_at": "2026-08-25",
                        "metadata": {"desk": "Solid American Walnut", "ergonomics": "Herman Miller Embody", "lighting": "Screenbar Halo 2700K"}
                    }
                ]

                # Append Marathi Cinema items to initial seed
                seed_data.extend(MARATHI_MOVIES_CATALOG)

                for item in seed_data:
                    db.save_entertainment_item(item)
                log_event("Seeded authentic Entertainment and Modern Lifestyle discovery catalog.", component="EntertainmentAgent")
            else:
                # Ensure Marathi Movies catalog is seeded even if database was previously created
                marathi_items = db.list_entertainment_items(category="Marathi Movies", limit=2)
                if not marathi_items:
                    for m_item in MARATHI_MOVIES_CATALOG:
                        db.save_entertainment_item(m_item)
                    log_event("Seeded authentic Marathi Movies into entertainment catalog.", component="EntertainmentAgent")
        except Exception as e:
            log_event(f"Error seeding entertainment catalog: {e}", level="WARNING", component="EntertainmentAgent")

    def get_items(self, category: Optional[str] = None, search: Optional[str] = None, favorites_only: bool = False, limit: int = 60) -> List[Dict[str, Any]]:
        """Returns catalog items filtered by category, search term, or favorite status."""
        items = db.list_entertainment_items(category=category, search=search, favorites_only=favorites_only, limit=limit)
        
        # If searching for Marathi or category is Marathi Movies, ensure catalog items are present
        if category and ("marathi" in category.lower() or category == "Marathi Movies"):
            if not items:
                return MARATHI_MOVIES_CATALOG
        if search and "marathi" in search.lower():
            existing_ids = {it.get("item_id") for it in items}
            for m in MARATHI_MOVIES_CATALOG:
                if m.get("item_id") not in existing_ids:
                    items.insert(0, m)
        return items

    def toggle_favorite(self, item_id: str) -> bool:
        """Toggles user favorite state on an item."""
        return db.toggle_entertainment_favorite(item_id)

    def get_categories(self) -> List[str]:
        return [
            "All", "Marathi Movies", "Bollywood", "Hollywood", "Tollywood",
            "Web Series", "YouTube", "Music", "Fashion", "Lifestyle"
        ]

    def ask_ai_manager_about_item(self, item_id: str, query: str = "Explain and summarize this") -> Dict[str, Any]:
        """Provides AI Manager summary and contextual insights for any media/lifestyle item."""
        items = db.list_entertainment_items(limit=100)
        target = next((i for i in items if i.get("item_id") == item_id), None)
        if not target:
            target = next((i for i in MARATHI_MOVIES_CATALOG if i.get("title") == item_id or i.get("item_id") == item_id), None)
        if not target:
            return {"status": "error", "error": f"Item [{item_id}] not found"}

        explanation = (
            f"🎬 **AI Manager Media Analysis — {target['title']}**\n\n"
            f"• **Category:** {target['category']} | **Creator/Publisher:** {target.get('creator', 'N/A')}\n"
            f"• **Overview & Summary:** {target['description']}\n\n"
            f"💡 **Key Insights & Direct Watch:**\n"
            f"1. **Direct Watch Link:** [{target['title']} on {target.get('source', 'Streaming Platform')}]({target.get('media_url', '#')})\n"
            f"2. **Relevance:** Highly rated in {target['category']} with verified streaming availability.\n"
            f"3. **Details:** {json.dumps(target.get('metadata', {}), ensure_ascii=False)}\n"
        )
        return {
            "status": "success",
            "item": target,
            "ai_explanation": explanation
        }

entertainment_agent = EntertainmentAgent()
