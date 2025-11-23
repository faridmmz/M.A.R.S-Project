"""
Contextual flavor text generator for turn results
Provides mission-specific narrative feedback
"""

import random
from typing import Literal


class FlavorTextGenerator:
    """Generates contextual flavor text based on mission type and outcome"""
    
    # Scientific Mission Success
    SCIENTIFIC_SUCCESS = [
        "Data downlink complete. 2 Patents filed.",
        "Experiment results exceed expectations. Research papers published.",
        "Payload successfully deployed. Scientific community celebrates breakthrough.",
        "Micro-gravity experiments yield groundbreaking data. Industry partnerships secured.",
        "Space-based manufacturing prototype operational. Commercial interest spikes.",
        "Biological samples processed successfully. Medical research advances.",
        "Telescope calibration perfect. Astronomical discoveries made.",
        "Zero-gravity crystal growth successful. Materials science breakthrough.",
    ]
    
    # Scientific Mission Failure
    SCIENTIFIC_FAILURE = [
        "Payload malfunction detected. Data loss significant.",
        "Communication blackout during critical phase. Experiment incomplete.",
        "Equipment failure in zero-gravity environment. Mission objectives not met.",
        "Radiation damage to sensitive instruments. Data corrupted.",
        "Orbital insertion error. Payload in wrong orbit.",
        "Power system failure. Experiments terminated early.",
        "Thermal regulation breakdown. Samples compromised.",
        "Navigation system error. Payload recovery delayed.",
    ]
    
    # Short Suborbital Success
    SHORT_SUBORBITAL_SUCCESS = [
        "Passengers report 'life-changing experience'. Reviews are stellar!",
        "Smooth flight profile. All passengers thrilled with zero-gravity moments.",
        "Perfect launch window. Passengers capture amazing space selfies.",
        "Mission flawless. Social media buzz generates new bookings.",
        "Passengers describe it as 'better than expected'. Word-of-mouth marketing gold.",
        "Celebrity passenger tweets go viral. Brand visibility skyrockets.",
        "Passengers return with glowing testimonials. Repeat bookings increase.",
        "Perfect weather conditions. Passengers experience stunning Earth views.",
    ]
    
    # Short Suborbital Failure
    SHORT_SUBORBITAL_FAILURE = [
        "Passengers experienced extreme G-force. Reviews are mixed.",
        "Technical issues during flight. Some passengers request refunds.",
        "Communication problems with ground control. Passenger anxiety high.",
        "Landing was rougher than expected. Minor injuries reported.",
        "Life support system glitch. Passengers uncomfortable but safe.",
        "Navigation error causes extended flight time. Passengers stressed.",
        "Equipment malfunction during zero-gravity phase. Experience compromised.",
        "Weather conditions worse than forecast. Turbulent re-entry.",
    ]
    
    # Long Orbital Success
    LONG_ORBITAL_SUCCESS = [
        "Extended stay successful. Passengers adapt well to space environment.",
        "Space station operations smooth. Passengers enjoy extended zero-gravity experience.",
        "All systems nominal. Passengers report transformative experience.",
        "Perfect orbital conditions. Passengers conduct personal experiments.",
        "Space station crew integration successful. Passengers feel like astronauts.",
        "Extended mission exceeds expectations. Passengers request longer stays.",
        "Orbital photography workshop successful. Passengers create stunning art.",
        "Space meditation sessions transformative. Passengers achieve deep relaxation.",
    ]
    
    # Long Orbital Failure
    LONG_ORBITAL_FAILURE = [
        "Life support system struggles with extended duration. Passengers uncomfortable.",
        "Orbital debris avoidance maneuvers stressful. Passengers anxious.",
        "Communication delays frustrate passengers. Isolation concerns rise.",
        "Extended zero-gravity causes health issues. Medical intervention required.",
        "Space station maintenance issues. Passengers experience disruptions.",
        "Orbital adjustment maneuvers cause motion sickness. Passengers struggling.",
        "Extended stay reveals equipment limitations. Passenger comfort compromised.",
        "Space weather impacts mission. Passengers experience increased radiation.",
    ]
    
    @staticmethod
    def generate_flavor_text(
        mission_type: Literal["Short_Suborbital", "Long_Orbital", "Scientific"],
        success: bool
    ) -> str:
        """
        Generate contextual flavor text based on mission type and outcome.
        
        Args:
            mission_type: Type of mission
            success: Whether mission succeeded
            
        Returns:
            Flavor text string
        """
        if mission_type == "Scientific":
            if success:
                return random.choice(FlavorTextGenerator.SCIENTIFIC_SUCCESS)
            else:
                return random.choice(FlavorTextGenerator.SCIENTIFIC_FAILURE)
        elif mission_type == "Short_Suborbital":
            if success:
                return random.choice(FlavorTextGenerator.SHORT_SUBORBITAL_SUCCESS)
            else:
                return random.choice(FlavorTextGenerator.SHORT_SUBORBITAL_FAILURE)
        elif mission_type == "Long_Orbital":
            if success:
                return random.choice(FlavorTextGenerator.LONG_ORBITAL_SUCCESS)
            else:
                return random.choice(FlavorTextGenerator.LONG_ORBITAL_FAILURE)
        else:
            if success:
                return "Mission completed successfully."
            else:
                return "Mission encountered difficulties."

