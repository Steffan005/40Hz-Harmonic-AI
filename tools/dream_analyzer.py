"""
DREAM ANALYSIS OFFICE - JUNGIAN SYMBOL INTERPRETATION
Phase 14.3: Symbol detection and thematic analysis
Interprets dreams through archetypal patterns
"""

from typing import Dict, List, Set
import re
import logging

logger = logging.getLogger(__name__)

class DreamAnalyzer:
    """
    Jungian dream analysis system
    Detects symbolic elements and identifies themes
    Provides reflection questions for deeper understanding
    """

    # Comprehensive symbol database
    SYMBOLS = {
        # WATER SYMBOLS
        'water': {
            'meanings': ['emotions', 'subconscious', 'purification', 'flow of life', 'unconscious mind'],
            'context': {
                'calm': 'emotional peace, clarity of feeling',
                'turbulent': 'emotional turmoil, inner conflict',
                'deep': 'hidden depths of psyche, profound emotions',
                'shallow': 'surface emotions, accessible feelings',
                'ocean': 'vast unconscious, collective unconscious',
                'river': 'journey of life, flow of time',
                'flood': 'overwhelming emotions, loss of control'
            }
        },
        'ocean': {
            'meanings': ['collective unconscious', 'vastness', 'unknown depths', 'primordial mother'],
            'context': {
                'calm': 'peace with the unknown',
                'stormy': 'chaos in the depths',
                'drowning': 'overwhelmed by unconscious'
            }
        },
        'river': {
            'meanings': ['life journey', 'flow', 'passage of time', 'direction'],
            'context': {
                'crossing': 'transition, threshold',
                'flowing': 'natural progression',
                'blocked': 'obstacles in life path'
            }
        },

        # FLYING SYMBOLS
        'flying': {
            'meanings': ['freedom', 'transcendence', 'escape', 'perspective', 'rising consciousness'],
            'context': {
                'effortless': 'confidence, mastery, spiritual elevation',
                'struggling': 'obstacles to transcendence, resistance',
                'falling': 'loss of control, fear of failure',
                'soaring': 'spiritual awakening, liberation'
            }
        },

        # DEATH & TRANSFORMATION
        'death': {
            'meanings': ['transformation', 'ending', 'rebirth', 'transition', 'ego death'],
            'context': {
                'own': 'major life transformation, ego transcendence',
                'loved one': 'relationship transformation, loss',
                'stranger': 'unknown aspect of self dying'
            }
        },
        'birth': {
            'meanings': ['new beginning', 'creation', 'potential', 'emergence'],
            'context': {
                'giving birth': 'creative project, new aspect of self',
                'witnessing': 'observing transformation',
                'difficult': 'challenging new beginning'
            }
        },

        # SHADOW SYMBOLS
        'snake': {
            'meanings': ['transformation', 'healing', 'shadow self', 'kundalini energy', 'primal instinct'],
            'context': {
                'shedding skin': 'renewal, letting go of old patterns',
                'attacking': 'confronting shadow, primal fear',
                'friendly': 'integrating instinctual wisdom'
            }
        },
        'shadow': {
            'meanings': ['repressed aspects', 'unknown self', 'denied traits', 'hidden power'],
            'context': {
                'pursuing': 'shadow integration needed',
                'hiding': 'avoidance of self',
                'embracing': 'shadow acceptance'
            }
        },

        # ANIMA/ANIMUS
        'woman': {
            'meanings': ['anima', 'feminine aspect', 'receptivity', 'intuition', 'nurturing'],
            'context': {
                'unknown': 'undeveloped feminine aspect',
                'wise': 'integrated anima',
                'dangerous': 'destructive feminine'
            }
        },
        'man': {
            'meanings': ['animus', 'masculine aspect', 'action', 'logic', 'authority'],
            'context': {
                'unknown': 'undeveloped masculine aspect',
                'wise': 'integrated animus',
                'threatening': 'destructive masculine'
            }
        },

        # HOUSE & HOME
        'house': {
            'meanings': ['self', 'psyche structure', 'ego', 'personality'],
            'context': {
                'basement': 'unconscious, hidden aspects',
                'attic': 'higher consciousness, forgotten memories',
                'room': 'aspect of personality',
                'abandoned': 'neglected self',
                'burning': 'transformation of self'
            }
        },

        # JOURNEY & QUEST
        'journey': {
            'meanings': ['life path', 'individuation', 'quest', 'search for meaning'],
            'context': {
                'lost': 'confusion about direction',
                'destination': 'goal or purpose',
                'companions': 'aspects of self or guides'
            }
        },
        'maze': {
            'meanings': ['confusion', 'complexity', 'search for center', 'initiation'],
            'context': {
                'lost': 'bewilderment, lack of direction',
                'finding center': 'discovering true self',
                'escaping': 'breaking free from confusion'
            }
        },

        # ANIMALS (ARCHETYPAL)
        'bird': {
            'meanings': ['spirit', 'transcendence', 'freedom', 'messenger', 'soul'],
            'context': {
                'flying': 'spiritual freedom',
                'caged': 'trapped spirit',
                'singing': 'joy, expression'
            }
        },
        'cat': {
            'meanings': ['independence', 'feminine mystery', 'intuition', 'magic'],
            'context': {
                'black': 'shadow wisdom, mystery',
                'friendly': 'integrated feminine intuition',
                'attacking': 'wild feminine energy'
            }
        },
        'dog': {
            'meanings': ['loyalty', 'instinct', 'protection', 'friendship', 'unconditional love'],
            'context': {
                'friendly': 'trusted instinct',
                'aggressive': 'threatening instincts',
                'lost': 'disconnected from instinctual wisdom'
            }
        },
        'wolf': {
            'meanings': ['wildness', 'instinct', 'pack mentality', 'predator', 'shadow'],
            'context': {
                'hunting': 'pursuing goals',
                'pack': 'group identity',
                'lone': 'individuation, isolation'
            }
        },

        # CONFLICT & SHADOW
        'fighting': {
            'meanings': ['inner conflict', 'struggle', 'integration', 'confrontation'],
            'context': {
                'winning': 'overcoming obstacle',
                'losing': 'defeated by shadow',
                'equal': 'ongoing struggle'
            }
        },
        'chase': {
            'meanings': ['avoidance', 'pursuit', 'shadow', 'fear'],
            'context': {
                'being chased': 'avoiding shadow or truth',
                'chasing': 'pursuing goal or aspect of self',
                'caught': 'confrontation inevitable'
            }
        }
    }

    # Thematic patterns
    THEMES = {
        'transformation': ['death', 'birth', 'butterfly', 'snake', 'shedding', 'phoenix', 'metamorphosis'],
        'journey': ['travel', 'road', 'path', 'bridge', 'quest', 'maze', 'walking', 'journey'],
        'conflict': ['fighting', 'war', 'battle', 'chase', 'enemy', 'struggle', 'conflict'],
        'connection': ['embrace', 'love', 'conversation', 'reunion', 'community', 'gathering', 'friend'],
        'transcendence': ['flying', 'ascending', 'mountain', 'summit', 'sky', 'heaven', 'enlightenment'],
        'shadow': ['darkness', 'hiding', 'monster', 'evil', 'fear', 'nightmare', 'shadow'],
        'creativity': ['painting', 'writing', 'creating', 'building', 'art', 'music', 'dance'],
        'loss': ['death', 'leaving', 'abandonment', 'lost', 'searching', 'missing', 'alone']
    }

    # Emotion keywords
    EMOTIONS = {
        'fear': ['scared', 'terrified', 'afraid', 'anxious', 'panic', 'dread', 'horror'],
        'joy': ['happy', 'excited', 'delighted', 'joyful', 'ecstatic', 'blissful', 'euphoric'],
        'sadness': ['sad', 'crying', 'mourning', 'depressed', 'grief', 'sorrow', 'melancholy'],
        'anger': ['angry', 'furious', 'rage', 'frustrated', 'mad', 'irritated', 'hostile'],
        'love': ['love', 'affection', 'tenderness', 'caring', 'compassion', 'warmth'],
        'confusion': ['confused', 'lost', 'uncertain', 'bewildered', 'disoriented', 'puzzled']
    }

    def __init__(self):
        """Initialize dream analysis system"""
        logger.info("💭 Dream Analysis Office initialized with Jungian framework")

    def analyze_dream(self, dream_text: str) -> Dict:
        """
        Comprehensive dream analysis

        Args:
            dream_text: The dream narrative

        Returns:
            Dict with symbols, themes, emotions, and interpretation
        """
        symbols_found = self._extract_symbols(dream_text)
        themes = self._identify_themes(symbols_found, dream_text)
        emotions = self._detect_emotions(dream_text)

        interpretation = self._generate_interpretation(symbols_found, themes, emotions)
        questions = self._generate_reflection_questions(themes)

        return {
            'dream_text': dream_text[:200] + '...' if len(dream_text) > 200 else dream_text,
            'symbols': symbols_found,
            'themes': themes,
            'emotions': emotions,
            'interpretation': interpretation,
            'reflection_questions': questions,
            'archetypal_analysis': self._archetypal_summary(symbols_found, themes)
        }

    def _extract_symbols(self, text: str) -> List[Dict]:
        """Find symbolic elements in dream text"""
        found = []
        text_lower = text.lower()

        for symbol, data in self.SYMBOLS.items():
            if symbol in text_lower or any(syn in text_lower for syn in [symbol + 's', symbol + 'ing']):
                # Detect context
                context = 'general'
                for ctx_key in data['context'].keys():
                    if ctx_key in text_lower:
                        context = ctx_key
                        break

                found.append({
                    'symbol': symbol,
                    'meanings': data['meanings'],
                    'context': context,
                    'context_interpretation': data['context'].get(context, 'general symbolism')
                })

        return found

    def _identify_themes(self, symbols: List[Dict], text: str) -> List[str]:
        """Extract overarching themes from symbols and text"""
        found_themes = set()
        text_lower = text.lower()

        # Check each theme's keywords
        for theme, keywords in self.THEMES.items():
            # Check if theme keywords appear in text
            if any(kw in text_lower for kw in keywords):
                found_themes.add(theme)

            # Check if symbols relate to theme
            for symbol in symbols:
                if any(kw in symbol['symbol'] for kw in keywords):
                    found_themes.add(theme)

        return list(found_themes)

    def _detect_emotions(self, text: str) -> List[str]:
        """Identify emotional tone of dream"""
        emotions = []
        text_lower = text.lower()

        for emotion, keywords in self.EMOTIONS.items():
            if any(kw in text_lower for kw in keywords):
                emotions.append(emotion)

        return emotions if emotions else ['neutral']

    def _generate_interpretation(self, symbols: List[Dict], themes: List[str], emotions: List[str]) -> str:
        """Create holistic dream interpretation"""
        lines = []

        lines.append("**Jungian Analysis:**\n")

        if themes:
            lines.append(f"This dream reveals themes of **{', '.join(themes)}**.")

        if symbols:
            lines.append(f"\nThe presence of {', '.join(s['symbol'] for s in symbols[:3])} suggests archetypal patterns:")
            for sym in symbols[:3]:  # Top 3 symbols
                lines.append(f"- **{sym['symbol'].title()}**: {', '.join(sym['meanings'][:2])}")
                if sym['context'] != 'general':
                    lines.append(f"  Context ({sym['context']}): {sym['context_interpretation']}")

        if emotions and emotions != ['neutral']:
            lines.append(f"\nThe emotional tone ({', '.join(emotions)}) indicates aspects of your psyche seeking conscious awareness.")

        lines.append("\nThis dream invites integration of unconscious material into consciousness through reflection and symbolic understanding.")

        return '\n'.join(lines)

    def _generate_reflection_questions(self, themes: List[str]) -> List[str]:
        """Suggest questions for deeper reflection"""
        questions = []

        question_map = {
            'transformation': "What in your life is currently changing or needs to change?",
            'journey': "What path are you currently on, and where does it lead?",
            'conflict': "What internal or external conflicts are you facing?",
            'connection': "What relationships or connections need your attention?",
            'transcendence': "What are you trying to rise above or transcend?",
            'shadow': "What aspects of yourself are you avoiding or denying?",
            'creativity': "What creative potential is trying to express itself?",
            'loss': "What are you mourning or letting go of?"
        }

        for theme in themes:
            if theme in question_map:
                questions.append(question_map[theme])

        if not questions:
            questions = [
                "What emotions did this dream evoke?",
                "Which dream element felt most significant?",
                "How does this dream relate to your waking life?"
            ]

        return questions

    def _archetypal_summary(self, symbols: List[Dict], themes: List[str]) -> str:
        """Generate archetypal pattern summary"""
        if not symbols:
            return "No clear archetypal patterns detected."

        archetypes = []

        # Check for hero's journey
        if 'journey' in themes or 'quest' in [s['symbol'] for s in symbols]:
            archetypes.append("Hero's Journey (individuation process)")

        # Check for shadow work
        if 'shadow' in themes or any(s['symbol'] in ['snake', 'monster', 'darkness'] for s in symbols):
            archetypes.append("Shadow Integration")

        # Check for anima/animus
        if any(s['symbol'] in ['woman', 'man'] for s in symbols):
            archetypes.append("Anima/Animus Encounter")

        # Check for death/rebirth
        if 'transformation' in themes or any(s['symbol'] in ['death', 'birth'] for s in symbols):
            archetypes.append("Death and Rebirth")

        if archetypes:
            return f"Archetypal patterns: {', '.join(archetypes)}"
        else:
            return "Personal symbolism predominant - specific to dreamer's life context."


# Singleton instance
dream_analyzer = DreamAnalyzer()
