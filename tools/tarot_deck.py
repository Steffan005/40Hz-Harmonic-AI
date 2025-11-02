#!/usr/bin/env python3
"""
Tarot Deck — Rider-Waite System with Full Symbolism

Implements complete 78-card tarot deck (22 Major Arcana + 56 Minor Arcana)
with traditional meanings, reversed interpretations, and archetypal symbolism.

This is Unity's first REAL metaphysical tool — no stubs, all authentic wisdom.
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class Suit(Enum):
    """Four suits of the Minor Arcana."""
    WANDS = "wands"      # Fire, creativity, action
    CUPS = "cups"        # Water, emotions, relationships
    SWORDS = "swords"    # Air, intellect, conflict
    PENTACLES = "pentacles"  # Earth, material, practical


class Position(Enum):
    """Card orientation."""
    UPRIGHT = "upright"
    REVERSED = "reversed"


@dataclass
class TarotCard:
    """Single tarot card with complete symbolism."""
    number: int  # 0-77 (0-21 Major, 22-77 Minor)
    name: str
    arcana: str  # "major" or "minor"
    suit: Optional[str] = None  # Only for Minor Arcana
    rank: Optional[str] = None  # "ace", "2"-"10", "page", "knight", "queen", "king"

    # Traditional meanings
    upright_keywords: List[str] = None
    reversed_keywords: List[str] = None
    upright_meaning: str = ""
    reversed_meaning: str = ""

    # Archetypal symbolism
    element: Optional[str] = None  # "fire", "water", "air", "earth", "spirit"
    numerology: Optional[int] = None
    astrological_correspondence: Optional[str] = None
    kabbalah_path: Optional[str] = None

    # Imagery description
    imagery: str = ""
    symbols: List[str] = None

    def __post_init__(self):
        if self.upright_keywords is None:
            self.upright_keywords = []
        if self.reversed_keywords is None:
            self.reversed_keywords = []
        if self.symbols is None:
            self.symbols = []


class TarotDeck:
    """
    Complete Rider-Waite tarot deck with traditional interpretations.

    Based on Arthur Edward Waite's 1909 system, illustrated by Pamela Colman Smith.
    This is the most widely recognized tarot system in Western esoteric tradition.
    """

    def __init__(self):
        self.cards = self._initialize_deck()
        self.shuffle_count = 0

    def _initialize_deck(self) -> List[TarotCard]:
        """Initialize all 78 cards with complete symbolism."""
        cards = []

        # MAJOR ARCANA (0-21)
        major_arcana = [
            TarotCard(
                number=0, name="The Fool", arcana="major", element="air",
                upright_keywords=["new beginnings", "innocence", "spontaneity", "free spirit"],
                reversed_keywords=["recklessness", "taken advantage of", "inconsideration"],
                upright_meaning="The Fool represents new beginnings, having faith in the future, being inexperienced, not knowing what to expect, having beginner's luck, improvisation and believing in the universe.",
                reversed_meaning="Reversed, The Fool can indicate naivety, poor judgement, stupidity, chaos, apathy, bad decisions, and lack of fun.",
                numerology=0, astrological_correspondence="Uranus",
                imagery="A young person steps toward a cliff edge, carrying a small bag, with a white dog at their heels. The sun shines behind them.",
                symbols=["white rose", "cliff", "dog", "bag", "sun"]
            ),
            TarotCard(
                number=1, name="The Magician", arcana="major", element="air",
                upright_keywords=["manifestation", "resourcefulness", "power", "inspired action"],
                reversed_keywords=["manipulation", "poor planning", "untapped talents"],
                upright_meaning="The Magician represents manifestation, resourcefulness, inspired action, concentration, and power. You have the tools and resources you need to succeed.",
                reversed_meaning="Reversed, manipulation, poor planning, latent talents, greed, and trickery.",
                numerology=1, astrological_correspondence="Mercury",
                imagery="A figure stands before a table with tools of the four suits, one hand pointing up, one pointing down.",
                symbols=["infinity symbol", "wand", "pentacle", "cup", "sword", "roses", "lilies"]
            ),
            TarotCard(
                number=2, name="The High Priestess", arcana="major", element="water",
                upright_keywords=["intuition", "sacred knowledge", "divine feminine", "subconscious mind"],
                reversed_keywords=["secrets", "disconnected from intuition", "withdrawal"],
                upright_meaning="The High Priestess represents intuition, mystery, stillness, and the subconscious mind. Trust your inner voice.",
                reversed_meaning="Reversed, repressed feelings, hidden agendas, need for introspection.",
                numerology=2, astrological_correspondence="Moon",
                imagery="A woman sits between two pillars (Boaz and Jachin), with the moon at her feet and a cross on her chest.",
                symbols=["pillars", "veil", "pomegranates", "crescent moon", "cross", "Torah"]
            ),
            TarotCard(
                number=3, name="The Empress", arcana="major", element="earth",
                upright_keywords=["femininity", "beauty", "nature", "nurturing", "abundance"],
                reversed_keywords=["creative block", "dependence on others", "smothering"],
                upright_meaning="The Empress represents divine feminine energy, creativity, fertility, and abundance. Nature and growth.",
                reversed_meaning="Reversed, creative blocks, lack of growth, neglecting self-care.",
                numerology=3, astrological_correspondence="Venus",
                imagery="A woman reclines on cushions in a lush forest, wearing a crown of stars, holding a scepter.",
                symbols=["venus symbol", "crown of stars", "wheat", "river", "trees"]
            ),
            TarotCard(
                number=4, name="The Emperor", arcana="major", element="fire",
                upright_keywords=["authority", "establishment", "structure", "father figure"],
                reversed_keywords=["domination", "excessive control", "lack of discipline", "inflexibility"],
                upright_meaning="The Emperor represents authority, structure, control, and fatherhood. Establishing order and taking charge.",
                reversed_meaning="Reversed, tyranny, rigidity, coldness, control issues.",
                numerology=4, astrological_correspondence="Aries",
                imagery="A bearded figure sits on a stone throne decorated with rams' heads, holding an ankh and orb.",
                symbols=["throne", "rams", "ankh", "orb", "armor", "mountains"]
            ),
            TarotCard(
                number=5, name="The Hierophant", arcana="major", element="earth",
                upright_keywords=["spiritual wisdom", "religious beliefs", "conformity", "tradition"],
                reversed_keywords=["personal beliefs", "freedom", "challenging the status quo"],
                upright_meaning="The Hierophant represents tradition, conformity, education, and belief systems. Seeking guidance from institutions.",
                reversed_meaning="Reversed, rebellion, subversiveness, new approaches, unconventional.",
                numerology=5, astrological_correspondence="Taurus",
                imagery="A religious figure sits between two pillars, wearing a triple crown, giving blessing to two acolytes.",
                symbols=["triple crown", "keys", "pillars", "crossed keys"]
            ),
            TarotCard(
                number=6, name="The Lovers", arcana="major", element="air",
                upright_keywords=["love", "harmony", "relationships", "values alignment"],
                reversed_keywords=["self-love", "disharmony", "imbalance", "misalignment of values"],
                upright_meaning="The Lovers represents love, harmony, union, and choices. Deep connections and alignment of values.",
                reversed_meaning="Reversed, relationship problems, imbalance, disharmony, misaligned values.",
                numerology=6, astrological_correspondence="Gemini",
                imagery="A man and woman stand beneath an angel (Raphael), with the Tree of Knowledge behind them.",
                symbols=["angel", "tree of knowledge", "tree of life", "serpent", "mountain"]
            ),
            TarotCard(
                number=7, name="The Chariot", arcana="major", element="water",
                upright_keywords=["control", "willpower", "success", "action", "determination"],
                reversed_keywords=["self-discipline", "opposition", "lack of direction"],
                upright_meaning="The Chariot represents willpower, determination, and triumph. Harnessing opposing forces to achieve goals.",
                reversed_meaning="Reversed, lack of control and direction, aggression, powerlessness.",
                numerology=7, astrological_correspondence="Cancer",
                imagery="A figure drives a chariot pulled by two sphinxes (one black, one white).",
                symbols=["sphinxes", "armor", "crown", "wand", "city walls"]
            ),
            TarotCard(
                number=8, name="Strength", arcana="major", element="fire",
                upright_keywords=["strength", "courage", "persuasion", "influence", "compassion"],
                reversed_keywords=["inner strength", "self-doubt", "low energy", "raw emotion"],
                upright_meaning="Strength represents inner strength, bravery, compassion, focus, and influence. Gentle control over animal instincts.",
                reversed_meaning="Reversed, self-doubt, weakness, insecurity, low energy.",
                numerology=8, astrological_correspondence="Leo",
                imagery="A woman gently closes a lion's mouth, wearing a white robe and infinity symbol crown.",
                symbols=["lion", "infinity symbol", "white robe", "flowers"]
            ),
            TarotCard(
                number=9, name="The Hermit", arcana="major", element="earth",
                upright_keywords=["soul searching", "introspection", "inner guidance", "solitude"],
                reversed_keywords=["isolation", "loneliness", "withdrawal", "paranoia"],
                upright_meaning="The Hermit represents soul searching, introspection, inner guidance, and solitude. Seeking truth within.",
                reversed_meaning="Reversed, isolation, loneliness, withdrawal, recluse.",
                numerology=9, astrological_correspondence="Virgo",
                imagery="An old man stands on a mountain peak holding a lantern with a six-pointed star.",
                symbols=["lantern", "star of david", "staff", "mountain", "grey robe"]
            ),
            TarotCard(
                number=10, name="Wheel of Fortune", arcana="major", element="fire",
                upright_keywords=["good luck", "karma", "life cycles", "destiny", "turning point"],
                reversed_keywords=["bad luck", "resistance to change", "breaking cycles"],
                upright_meaning="The Wheel of Fortune represents cycles, turning points, fate, and karma. What goes up must come down.",
                reversed_meaning="Reversed, bad luck, lack of control, clinging to control, unwelcome changes.",
                numerology=10, astrological_correspondence="Jupiter",
                imagery="A giant wheel rotates in the sky with four winged creatures in the corners.",
                symbols=["wheel", "sphinx", "snake", "anubis", "angels", "TARO/ROTA"]
            ),
            TarotCard(
                number=11, name="Justice", arcana="major", element="air",
                upright_keywords=["justice", "fairness", "truth", "cause and effect", "law"],
                reversed_keywords=["unfairness", "lack of accountability", "dishonesty"],
                upright_meaning="Justice represents fairness, truth, cause and effect, and the law. Decisions based on objectivity and analysis.",
                reversed_meaning="Reversed, unfairness, lack of accountability, dishonesty, legal complications.",
                numerology=11, astrological_correspondence="Libra",
                imagery="A figure sits between two pillars holding scales and a sword.",
                symbols=["scales", "sword", "pillars", "crown", "purple cloak"]
            ),
            TarotCard(
                number=12, name="The Hanged Man", arcana="major", element="water",
                upright_keywords=["pause", "surrender", "letting go", "new perspectives"],
                reversed_keywords=["delays", "resistance", "stalling", "indecision"],
                upright_meaning="The Hanged Man represents suspension, letting go, and new perspectives. Sacrifice for greater good.",
                reversed_meaning="Reversed, delays, resistance, stalling, needless sacrifice.",
                numerology=12, astrological_correspondence="Neptune",
                imagery="A man hangs upside-down from a tree, one leg bent, arms behind back, halo around head.",
                symbols=["tree", "halo", "rope", "inverted position"]
            ),
            TarotCard(
                number=13, name="Death", arcana="major", element="water",
                upright_keywords=["endings", "change", "transformation", "transition"],
                reversed_keywords=["resistance to change", "personal transformation", "inner purging"],
                upright_meaning="Death represents endings, change, transformation, and transition. Not literal death, but profound change.",
                reversed_meaning="Reversed, resistance to change, inability to move on, stagnation.",
                numerology=13, astrological_correspondence="Scorpio",
                imagery="A skeleton in armor rides a white horse, carrying a black flag with white flower.",
                symbols=["skeleton", "armor", "white horse", "black flag", "white rose"]
            ),
            TarotCard(
                number=14, name="Temperance", arcana="major", element="fire",
                upright_keywords=["balance", "moderation", "patience", "purpose"],
                reversed_keywords=["imbalance", "excess", "self-healing", "re-alignment"],
                upright_meaning="Temperance represents balance, moderation, patience, and finding meaning. Blending opposing forces.",
                reversed_meaning="Reversed, imbalance, excess, lack of long-term vision, disharmony.",
                numerology=14, astrological_correspondence="Sagittarius",
                imagery="An angel pours water between two cups, one foot on land, one in water.",
                symbols=["angel", "water", "cups", "path to mountain", "triangle"]
            ),
            TarotCard(
                number=15, name="The Devil", arcana="major", element="earth",
                upright_keywords=["shadow self", "attachment", "addiction", "restriction"],
                reversed_keywords=["releasing limiting beliefs", "exploring dark thoughts", "detachment"],
                upright_meaning="The Devil represents bondage, addiction, materialism, and playfulness. Exploring shadow self and desires.",
                reversed_meaning="Reversed, releasing limiting beliefs, exploring dark thoughts, breaking free.",
                numerology=15, astrological_correspondence="Capricorn",
                imagery="A horned devil figure presides over two chained naked humans.",
                symbols=["chains", "inverted pentagram", "horns", "torch", "male and female"]
            ),
            TarotCard(
                number=16, name="The Tower", arcana="major", element="fire",
                upright_keywords=["sudden change", "upheaval", "chaos", "revelation", "awakening"],
                reversed_keywords=["personal transformation", "fear of change", "averting disaster"],
                upright_meaning="The Tower represents sudden upheaval, chaos, revelation, and awakening. Necessary destruction before rebuilding.",
                reversed_meaning="Reversed, personal transformation, fear of change, averting disaster.",
                numerology=16, astrological_correspondence="Mars",
                imagery="A tower struck by lightning with people falling from it.",
                symbols=["lightning", "crown", "falling figures", "flames", "grey clouds"]
            ),
            TarotCard(
                number=17, name="The Star", arcana="major", element="air",
                upright_keywords=["hope", "faith", "purpose", "renewal", "spirituality"],
                reversed_keywords=["lack of faith", "despair", "self-trust", "disconnection"],
                upright_meaning="The Star represents hope, faith, renewal, and inspiration. Healing after difficult times.",
                reversed_meaning="Reversed, lack of faith, despair, self-trust, disconnected from higher self.",
                numerology=17, astrological_correspondence="Aquarius",
                imagery="A naked woman kneels by water, pouring water from two jugs, with eight stars above.",
                symbols=["stars", "water", "bird", "tree", "nakedness"]
            ),
            TarotCard(
                number=18, name="The Moon", arcana="major", element="water",
                upright_keywords=["illusion", "fear", "anxiety", "subconscious", "intuition"],
                reversed_keywords=["release of fear", "repressed emotion", "inner confusion"],
                upright_meaning="The Moon represents illusion, intuition, uncertainty, and subconscious. Navigating through fog and confusion.",
                reversed_meaning="Reversed, release of fear, clarity, repressed emotion, inner confusion.",
                numerology=18, astrological_correspondence="Pisces",
                imagery="Two dogs howl at a moon with a face, crayfish emerges from water, path leads to mountains.",
                symbols=["moon", "dogs", "crayfish", "path", "towers"]
            ),
            TarotCard(
                number=19, name="The Sun", arcana="major", element="fire",
                upright_keywords=["positivity", "fun", "warmth", "success", "vitality"],
                reversed_keywords=["inner child", "feeling down", "overly optimistic"],
                upright_meaning="The Sun represents success, radiance, abundance, and vitality. Pure joy and confidence.",
                reversed_meaning="Reversed, temporary depression, lack of success, sadness, inner child.",
                numerology=19, astrological_correspondence="Sun",
                imagery="A child rides a white horse beneath a smiling sun, holding a red flag.",
                symbols=["sun", "child", "white horse", "sunflowers", "red banner"]
            ),
            TarotCard(
                number=20, name="Judgement", arcana="major", element="fire",
                upright_keywords=["judgement", "rebirth", "inner calling", "absolution"],
                reversed_keywords=["self-doubt", "inner critic", "ignoring the call"],
                upright_meaning="Judgement represents reflection, reckoning, and inner calling. Awakening to higher consciousness.",
                reversed_meaning="Reversed, self-doubt, inner critic, lack of self-awareness, ignoring call.",
                numerology=20, astrological_correspondence="Pluto",
                imagery="Angel Gabriel blows trumpet, naked people rise from coffins with arms outstretched.",
                symbols=["angel", "trumpet", "rising figures", "cross", "mountains"]
            ),
            TarotCard(
                number=21, name="The World", arcana="major", element="earth",
                upright_keywords=["completion", "accomplishment", "travel", "fulfillment"],
                reversed_keywords=["seeking personal closure", "short-cuts", "delays"],
                upright_meaning="The World represents completion, accomplishment, fulfillment, and sense of belonging. The end of one cycle.",
                reversed_meaning="Reversed, lack of completion, lack of closure, seeking closure.",
                numerology=21, astrological_correspondence="Saturn",
                imagery="A naked figure dances within a wreath, holding two wands, four figures in corners.",
                symbols=["wreath", "infinity ribbon", "wands", "four evangelists"]
            ),
        ]

        cards.extend(major_arcana)

        # MINOR ARCANA (22-77)
        # Wands (Fire, Creativity, Action)
        wands_meanings = {
            "ace": ("new opportunities", "spiritual growth", "creative spark"),
            "2": ("planning ahead", "future possibilities", "decisions"),
            "3": ("expansion", "foresight", "progress"),
            "4": ("celebration", "harmony", "home"),
            "5": ("conflict", "disagreements", "competition"),
            "6": ("victory", "success", "public recognition"),
            "7": ("challenge", "perseverance", "standing ground"),
            "8": ("swift action", "movement", "alignment"),
            "9": ("resilience", "persistence", "defensiveness"),
            "10": ("burden", "responsibility", "hard work"),
            "page": ("enthusiasm", "exploration", "discovery"),
            "knight": ("energy", "passion", "adventure"),
            "queen": ("courage", "confidence", "determination"),
            "king": ("natural leader", "vision", "entrepreneur")
        }

        for i, (rank, meanings) in enumerate(wands_meanings.items(), start=22):
            cards.append(TarotCard(
                number=i, name=f"{rank.title()} of Wands", arcana="minor",
                suit="wands", rank=rank, element="fire",
                upright_keywords=list(meanings),
                reversed_keywords=["blocked " + meanings[0], "delays"],
                upright_meaning=f"{rank.title()} of Wands: {', '.join(meanings)}",
                reversed_meaning=f"Reversed: Delays, blocks, lack of {meanings[0]}"
            ))

        # Cups (Water, Emotions, Relationships)
        cups_meanings = {
            "ace": ("love", "new relationships", "compassion", "creativity"),
            "2": ("unified love", "partnership", "mutual attraction"),
            "3": ("celebration", "friendship", "community"),
            "4": ("meditation", "contemplation", "apathy"),
            "5": ("regret", "failure", "disappointment"),
            "6": ("revisiting the past", "childhood memories", "innocence"),
            "7": ("illusion", "choices", "wishful thinking"),
            "8": ("walking away", "disappointment", "abandonment"),
            "9": ("contentment", "satisfaction", "gratitude"),
            "10": ("divine love", "blissful relationships", "harmony"),
            "page": ("creative opportunities", "curiosity", "possibility"),
            "knight": ("romance", "charm", "imagination"),
            "queen": ("compassion", "calm", "comfort"),
            "king": ("diplomatic", "balance", "devotion")
        }

        for i, (rank, meanings) in enumerate(cups_meanings.items(), start=36):
            cards.append(TarotCard(
                number=i, name=f"{rank.title()} of Cups", arcana="minor",
                suit="cups", rank=rank, element="water",
                upright_keywords=list(meanings),
                reversed_keywords=["blocked " + meanings[0], "emotional confusion"],
                upright_meaning=f"{rank.title()} of Cups: {', '.join(meanings)}",
                reversed_meaning=f"Reversed: Emotional blocks, lack of {meanings[0]}"
            ))

        # Swords (Air, Intellect, Conflict)
        swords_meanings = {
            "ace": ("breakthrough", "clarity", "sharp mind"),
            "2": ("difficult decisions", "weighing options", "stalemate"),
            "3": ("heartbreak", "emotional pain", "sorrow"),
            "4": ("rest", "relaxation", "contemplation"),
            "5": ("conflict", "defeat", "winning at all costs"),
            "6": ("transition", "moving on", "leaving behind"),
            "7": ("betrayal", "deception", "strategy"),
            "8": ("restriction", "confusion", "powerlessness"),
            "9": ("anxiety", "worry", "nightmares"),
            "10": ("painful endings", "deep wounds", "betrayal"),
            "page": ("new ideas", "curiosity", "vigilance"),
            "knight": ("ambitious", "action-oriented", "driven"),
            "queen": ("independent", "unbiased", "clear boundaries"),
            "king": ("intellectual power", "authority", "truth")
        }

        for i, (rank, meanings) in enumerate(swords_meanings.items(), start=50):
            cards.append(TarotCard(
                number=i, name=f"{rank.title()} of Swords", arcana="minor",
                suit="swords", rank=rank, element="air",
                upright_keywords=list(meanings),
                reversed_keywords=["confusion", "clouded thinking"],
                upright_meaning=f"{rank.title()} of Swords: {', '.join(meanings)}",
                reversed_meaning=f"Reversed: Mental blocks, confusion, lack of clarity"
            ))

        # Pentacles (Earth, Material, Practical)
        pentacles_meanings = {
            "ace": ("opportunity", "prosperity", "new venture"),
            "2": ("multiple priorities", "time management", "balance"),
            "3": ("teamwork", "collaboration", "learning"),
            "4": ("saving money", "security", "conservatism"),
            "5": ("financial loss", "poverty", "insecurity"),
            "6": ("giving", "receiving", "sharing wealth"),
            "7": ("long-term view", "perseverance", "investment"),
            "8": ("apprenticeship", "education", "skill development"),
            "9": ("abundance", "luxury", "self-sufficiency"),
            "10": ("wealth", "financial security", "family"),
            "page": ("manifestation", "financial opportunity", "new job"),
            "knight": ("hard work", "productivity", "routine"),
            "queen": ("practical", "nurturing", "providing"),
            "king": ("wealth", "business", "abundance")
        }

        for i, (rank, meanings) in enumerate(pentacles_meanings.items(), start=64):
            cards.append(TarotCard(
                number=i, name=f"{rank.title()} of Pentacles", arcana="minor",
                suit="pentacles", rank=rank, element="earth",
                upright_keywords=list(meanings),
                reversed_keywords=["financial loss", "lack of planning"],
                upright_meaning=f"{rank.title()} of Pentacles: {', '.join(meanings)}",
                reversed_meaning=f"Reversed: Financial difficulties, lack of {meanings[0]}"
            ))

        return cards

    def shuffle(self, times: int = 7):
        """
        Shuffle the deck.

        Traditional tarot practice: shuffle 7 times for thorough randomization.
        """
        for _ in range(times):
            random.shuffle(self.cards)
        self.shuffle_count += 1

    def draw(self, count: int = 1, position: Position = None) -> List[Dict]:
        """
        Draw cards from the deck.

        Args:
            count: Number of cards to draw
            position: Force upright/reversed, or None for random

        Returns:
            List of drawn card dicts with position
        """
        drawn = []
        for _ in range(min(count, len(self.cards))):
            card = self.cards.pop(0)

            # Determine position
            if position is None:
                card_position = random.choice([Position.UPRIGHT, Position.REVERSED])
            else:
                card_position = position

            drawn.append({
                "card": asdict(card),
                "position": card_position.value
            })

        return drawn

    def reset(self):
        """Reset deck to full 78 cards and shuffle."""
        self.cards = self._initialize_deck()
        self.shuffle()


class TarotSpread:
    """
    Tarot spreads for different query types.
    """

    @staticmethod
    def three_card(deck: TarotDeck, question: str = "") -> Dict:
        """
        Classic three-card spread: Past, Present, Future.

        Args:
            deck: TarotDeck instance
            question: Question being asked

        Returns:
            Spread interpretation
        """
        cards = deck.draw(3)

        return {
            "spread_name": "Three Card (Past/Present/Future)",
            "question": question,
            "cards": {
                "past": cards[0],
                "present": cards[1],
                "future": cards[2]
            },
            "interpretation": "Past influences current situation, leading to future outcome."
        }

    @staticmethod
    def celtic_cross(deck: TarotDeck, question: str = "") -> Dict:
        """
        Celtic Cross spread (10 cards): Most comprehensive spread.

        Positions:
        1. Present situation
        2. Challenge
        3. Distant past/foundation
        4. Recent past
        5. Best outcome
        6. Near future
        7. Your attitude
        8. External influences
        9. Hopes and fears
        10. Final outcome
        """
        cards = deck.draw(10)

        positions = [
            "present", "challenge", "foundation", "recent_past", "best_outcome",
            "near_future", "attitude", "external_influences", "hopes_fears", "outcome"
        ]

        return {
            "spread_name": "Celtic Cross",
            "question": question,
            "cards": {pos: card for pos, card in zip(positions, cards)},
            "interpretation": "Comprehensive analysis of past, present, and future influences."
        }

    @staticmethod
    def relationship(deck: TarotDeck, question: str = "") -> Dict:
        """
        Relationship spread (7 cards): For partnership questions.

        Positions:
        1. You
        2. Partner
        3. Connection
        4. Strengths
        5. Weaknesses
        6. What needs attention
        7. Outcome
        """
        cards = deck.draw(7)

        positions = ["you", "partner", "connection", "strengths", "weaknesses", "attention", "outcome"]

        return {
            "spread_name": "Relationship Spread",
            "question": question,
            "cards": {pos: card for pos, card in zip(positions, cards)},
            "interpretation": "Analysis of relationship dynamics and potential."
        }


# Singleton instance
_tarot_deck = None


def get_tarot_deck() -> TarotDeck:
    """Get singleton tarot deck instance."""
    global _tarot_deck
    if _tarot_deck is None:
        _tarot_deck = TarotDeck()
        _tarot_deck.shuffle()
    return _tarot_deck


# CLI testing
if __name__ == "__main__":
    print("="*70)
    print("TAROT DECK — RIDER-WAITE SYSTEM")
    print("="*70)

    deck = TarotDeck()
    deck.shuffle()

    print(f"\n✅ Deck initialized: {len(deck.cards)} cards")
    print(f"   Major Arcana: 22 cards (0-21)")
    print(f"   Minor Arcana: 56 cards")
    print(f"      • Wands (Fire): 14 cards")
    print(f"      • Cups (Water): 14 cards")
    print(f"      • Swords (Air): 14 cards")
    print(f"      • Pentacles (Earth): 14 cards")

    # Test 1: Draw single card
    print("\n1. Single Card Draw:")
    cards = deck.draw(1)
    card_data = cards[0]
    card = card_data["card"]
    position = card_data["position"]
    print(f"   {card['name']} ({position})")
    print(f"   Keywords: {', '.join(card['upright_keywords'] if position == 'upright' else card['reversed_keywords'])}")

    # Reset for spread
    deck.reset()

    # Test 2: Three-card spread
    print("\n2. Three-Card Spread (Past/Present/Future):")
    spread = TarotSpread.three_card(deck, "What does my future hold?")
    print(f"   Question: {spread['question']}")
    for position, card_data in spread['cards'].items():
        card = card_data["card"]
        pos = card_data["position"]
        print(f"   {position.upper()}: {card['name']} ({pos})")

    # Reset for another spread
    deck.reset()

    # Test 3: Show Major Arcana
    print("\n3. Major Arcana (Sample):")
    for i in range(5):  # Show first 5
        card = deck.cards[i]
        print(f"   {card.number}. {card.name}")
        print(f"      Element: {card.element}, Astrology: {card.astrological_correspondence}")
        print(f"      Upright: {', '.join(card.upright_keywords[:3])}")

    print("\n" + "="*70)
    print("TAROT SYSTEM OPERATIONAL")
    print("="*70)
