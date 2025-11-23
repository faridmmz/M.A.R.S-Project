"""
News Generator for M.A.R.S. Project
Generates contextual news based on mission type, year, and game state
"""

import random
from typing import Literal


class NewsGenerator:
    """Generates diverse news content for different mission types and scenarios"""
    
    # Scientific Mission News
    SCIENTIFIC_NEWS = [
        "NASA announces new grants for micro-gravity bio-research. Scientific missions highly profitable this quarter.",
        "ESA partners with private sector for space station experiments. High demand for scientific payloads.",
        "Breakthrough in zero-gravity manufacturing. Industrial space contracts on the rise.",
        "International Space Station opens new research slots. Scientific missions in high demand.",
        "Pharmaceutical companies invest heavily in space-based research. Premium rates for scientific missions.",
        "Space-based telescope maintenance contracts available. Steady income for scientific missions.",
        "Mars sample return mission requires Earth-based testing. Scientific missions critical this year.",
        "Asteroid mining companies seek orbital processing facilities. Scientific missions see increased funding.",
    ]
    
    # Short Suborbital News
    SHORT_SUBORBITAL_NEWS = [
        "Influencer 'StarBoy' live-streams from orbit; suborbital demand spikes! Tourist missions trending.",
        "Celebrity space tourism boom continues. Short suborbital flights see record bookings.",
        "Corporate team-building events move to space. High demand for short orbital experiences.",
        "Space wedding trend takes off. Short suborbital missions booked months in advance.",
        "Reality TV show 'Space Survivor' drives tourism. Short missions see 300% demand increase.",
        "Tech billionaires compete for fastest space trip. Short suborbital flights in high demand.",
        "Space photography workshops become popular. Short missions perfect for content creators.",
        "Zero-gravity fitness trend emerges. Short orbital stays see increased interest.",
    ]
    
    # Long Orbital News
    LONG_ORBITAL_NEWS = [
        "Luxury space hotels announce expansion. Long orbital stays see premium pricing.",
        "Space honeymoon packages launch. Extended orbital missions in high demand.",
        "Corporate retreats move to space stations. Long orbital stays booked solid.",
        "Space artist residency programs begin. Long missions attract creative professionals.",
        "Space therapy sessions gain popularity. Extended orbital stays see steady demand.",
        "Space education programs expand. Long missions perfect for immersive learning.",
        "Space retirement communities planned. Long orbital stays see growing interest.",
        "Space meditation retreats launch. Extended missions attract wellness enthusiasts.",
    ]
    
    # Crisis News (affects all missions, especially Scientific)
    CRISIS_NEWS = [
        "Solar flare warning: High risk for electronic payloads. Scientific missions face increased failure rates.",
        "Space debris field detected near common orbits. All missions face elevated risk this quarter.",
        "Geomagnetic storm alert: Satellite communications disrupted. Mission reliability concerns rise.",
        "Asteroid near-miss causes orbital adjustments. Launch windows reduced for all mission types.",
        "Space weather advisory: Increased radiation levels. Scientific payloads at higher risk.",
        "Orbital traffic congestion reaches critical levels. Launch delays affect all mission types.",
        "International space regulations tighten. Compliance costs rise for all missions.",
        "Space insurance premiums spike after recent incidents. All missions face higher costs.",
    ]
    
    # General Market News
    GENERAL_NEWS = [
        "Space industry sees record investment. Market conditions favorable for all mission types.",
        "New spaceport opens, increasing launch capacity. More opportunities for all missions.",
        "Space tourism market matures. Steady demand across all mission categories.",
        "Government space contracts increase. Scientific and commercial missions benefit.",
        "Space economy reaches $1 trillion milestone. All mission types see growth potential.",
        "International space cooperation expands. More opportunities for commercial missions.",
        "Space technology costs continue to decrease. Profit margins improve for all missions.",
        "Space sustainability initiatives gain traction. Green missions receive premium pricing.",
    ]
    
    # Funny Space Jokes
    SPACE_JOKES = [
        "Why don't aliens visit Earth? Because they heard the WiFi password is 'password123'.",
        "What do you call a nosy pepper? Jalapeño business! 🚀",
        "Why did the astronaut break up with his girlfriend? He needed space!",
        "How do you organize a space party? You planet!",
        "What's an astronaut's favorite part of a computer? The space bar!",
        "Why don't scientists trust atoms? Because they make up everything!",
        "What did Mars say to Saturn? Give me a ring sometime!",
        "Why did the sun go to school? To get brighter!",
        "What's a spaceman's favorite candy? Mars bars!",
        "Why did the rocket break up? It had too much space between them!",
        "What do you call a fake noodle? An impasta! 🛸",
        "Why don't aliens ever get lost? They always use GPS (Galactic Positioning System)!",
        "What's a comet's favorite drink? Meteor shower!",
        "Why did the moon break up with the sun? It needed some space!",
        "What do you call a sleeping bull? A bulldozer! 🚀",
    ]
    
    @staticmethod
    def generate_competitor_prices(
        short_suborbital_price: float,
        long_orbital_price: float,
        scientific_price: float
    ) -> str:
        """
        Generate competitor price news for all three mission types.
        
        Args:
            short_suborbital_price: Competitor price for short suborbital
            long_orbital_price: Competitor price for long orbital
            scientific_price: Competitor price for scientific
            
        Returns:
            News string with competitor prices
        """
        return f"Market Update: Short Suborbital €{short_suborbital_price/1_000:.0f}k | Long Orbital €{long_orbital_price/1_000_000:.1f}M | Scientific €{scientific_price/1_000_000:.1f}M"
    
    @staticmethod
    def generate_news_feed(
        mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"],
        turn_number: int,
        short_suborbital_price: float,
        long_orbital_price: float,
        scientific_price: float,
        num_items: int = 5
    ) -> list[str]:
        """
        Generate a feed of news items including competitor prices and jokes.
        
        Args:
            mission_type: Current mission type
            turn_number: Current turn
            short_suborbital_price: Competitor price for short suborbital
            long_orbital_price: Competitor price for long orbital
            scientific_price: Competitor price for scientific
            num_items: Number of news items to generate
            
        Returns:
            List of news items
        """
        feed = []
        
        # Always include competitor prices
        feed.append(NewsGenerator.generate_competitor_prices(
            short_suborbital_price,
            long_orbital_price,
            scientific_price
        ))
        
        # Add mission-specific news
        feed.append(NewsGenerator.generate_news(mission_type, turn_number, include_crisis=True))
        
        # Add a joke (30% chance per item)
        if random.random() < 0.3:
            feed.append(f"💡 {random.choice(NewsGenerator.SPACE_JOKES)}")
        
        # Add general market news
        if random.random() < 0.4:
            feed.append(random.choice(NewsGenerator.GENERAL_NEWS))
        
        # Add news from other mission types for variety
        other_types = ["Short_Suborbital", "Long_Orbital", "Scientific"]
        if mission_type in other_types:
            other_types.remove(mission_type)
        if random.random() < 0.3 and other_types:
            feed.append(NewsGenerator.generate_news(random.choice(other_types), turn_number, include_crisis=False))
        
        # Fill remaining slots with mix of content
        while len(feed) < num_items:
            rand = random.random()
            if rand < 0.2:
                feed.append(f"💡 {random.choice(NewsGenerator.SPACE_JOKES)}")
            elif rand < 0.5:
                feed.append(random.choice(NewsGenerator.GENERAL_NEWS))
            elif rand < 0.7:
                feed.append(NewsGenerator.generate_news(mission_type, turn_number, include_crisis=False))
            else:
                if other_types:
                    feed.append(NewsGenerator.generate_news(random.choice(other_types), turn_number, include_crisis=False))
        
        return feed[:num_items]
    
    @staticmethod
    def generate_news(
        mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"],
        turn_number: int,
        include_crisis: bool = False
    ) -> str:
        """
        Generate news based on mission type and turn number.
        
        Args:
            mission_type: Type of mission being planned
            turn_number: Current turn/year
            include_crisis: Whether to include crisis news (random chance)
            
        Returns:
            News headline string
        """
        # 20% chance of crisis news (if enabled)
        if include_crisis and random.random() < 0.2:
            return random.choice(NewsGenerator.CRISIS_NEWS)
        
        # Select news based on mission type
        if mission_type == "Scientific":
            news_pool = NewsGenerator.SCIENTIFIC_NEWS
        elif mission_type == "Short_Suborbital":
            news_pool = NewsGenerator.SHORT_SUBORBITAL_NEWS
        elif mission_type == "Long_Orbital":
            news_pool = NewsGenerator.LONG_ORBITAL_NEWS
        else:
            news_pool = NewsGenerator.GENERAL_NEWS
        
        # Occasionally mix in general news (30% chance)
        if random.random() < 0.3:
            return random.choice(NewsGenerator.GENERAL_NEWS)
        
        return random.choice(news_pool)
    
    @staticmethod
    def generate_turn_news(
        mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"],
        turn_number: int,
        previous_mission_type: str = None
    ) -> list[str]:
        """
        Generate multiple news items for a turn.
        
        Args:
            mission_type: Current mission type
            turn_number: Current turn
            previous_mission_type: Previous mission type (for variety)
            
        Returns:
            List of news headlines
        """
        news_items = []
        
        # Primary news based on current mission
        news_items.append(NewsGenerator.generate_news(mission_type, turn_number, include_crisis=True))
        
        # Occasionally add a second news item (30% chance)
        if random.random() < 0.3:
            # Mix in news from other mission types for variety
            if previous_mission_type and previous_mission_type != mission_type:
                news_items.append(NewsGenerator.generate_news(previous_mission_type, turn_number, include_crisis=False))
            else:
                # Random other mission type
                other_types = ["Short_Suborbital", "Long_Orbital", "Scientific"]
                other_types.remove(mission_type)
                news_items.append(NewsGenerator.generate_news(random.choice(other_types), turn_number, include_crisis=False))
        
        return news_items

