"""Confusion Detection System for Patient Responses

Analyzes patient responses for signals of confusion or lack of comprehension.
Combines text-based and audio-based (from Whisper) signals.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ConfusionSignal:
    """Represents a detected confusion signal"""
    signal_type: str
    description: str
    score_impact: int
    evidence: str

class ConfusionDetector:
    """
    Detects confusion in patient responses using multiple signals.
    
    Scoring System:
    - Short response (<5 words): +1 point
    - Uncertainty words: +2 points each
    - Vague language: +1 point each
    - Question instead of answer: +2 points
    - Low confidence (audio): +1 point
    - High filler word ratio: +1 point
    
    Threshold: ≥3 points = confused
    """
    
    # Uncertainty markers by language
    UNCERTAINTY_WORDS = {
        'en': [
            'maybe', 'i think', 'i guess', 'probably', 'perhaps',
            'not sure', 'i dont know', 'kind of', 'sort of',
            'might be', 'could be'
        ],
        'es': [
            'creo que', 'tal vez', 'quizás', 'probablemente',
            'no sé', 'no estoy seguro', 'puede ser', 'supongo',
            'más o menos', 'algo así'
        ],
        'it': [
            'credo', 'forse', 'probabilmente', 'non so',
            'non sono sicuro', 'può essere', 'più o meno',
            'penso che', 'direi'
        ]
    }
    
    # Vague/filler words by language
    VAGUE_WORDS = {
        'en': [
            'something', 'thing', 'stuff', 'whatever', 'somehow',
            'like', 'you know', 'um', 'uh', 'er', 'ah'
        ],
        'es': [
            'algo', 'cosa', 'cosas', 'pues', 'este', 'eh',
            'este', 'bueno', 'entonces', 'o sea'
        ],
        'it': [
            'qualcosa', 'cosa', 'roba', 'tipo', 'ecco',
            'eh', 'uhm', 'insomma', 'cioè', 'diciamo'
        ]
    }
    
    def __init__(self):
        """Initialize confusion detector"""
        self.confusion_threshold = 3  # Points needed to trigger confusion
    
    def detect_confusion(
        self,
        patient_response: str,
        language: str = 'en',
        audio_confidence: Optional[float] = None,
        is_comprehension_question: bool = False
    ) -> Dict:
        """
        Analyze patient response for confusion signals
        
        Args:
            patient_response: Patient's text response
            language: Language code (en, es, it)
            audio_confidence: Whisper confidence score (0-1)
            is_comprehension_question: Whether this was a comprehension check
        
        Returns:
            Dict with confusion analysis results
        """
        signals = []
        score = 0
        
        # Normalize text for analysis
        text = patient_response.lower().strip()
        word_count = len(text.split())
        
        # SIGNAL 1: Very short response (<5 words)
        if word_count < 5 and is_comprehension_question:
            signal = ConfusionSignal(
                signal_type='short_response',
                description='Response too brief for comprehension question',
                score_impact=1,
                evidence=f'Only {word_count} words'
            )
            signals.append(signal)
            score += signal.score_impact
        
        # SIGNAL 2: Uncertainty words
        uncertainty_found = self._find_patterns(
            text,
            self.UNCERTAINTY_WORDS.get(language, [])
        )
        if uncertainty_found:
            for word in uncertainty_found:
                signal = ConfusionSignal(
                    signal_type='uncertainty',
                    description='Expresses uncertainty',
                    score_impact=2,
                    evidence=f'Contains "{word}"'
                )
                signals.append(signal)
                score += signal.score_impact
        
        # SIGNAL 3: Vague language
        vague_found = self._find_patterns(
            text,
            self.VAGUE_WORDS.get(language, [])
        )
        if vague_found:
            for word in vague_found[:2]:  # Limit to first 2 to avoid over-counting
                signal = ConfusionSignal(
                    signal_type='vague_language',
                    description='Uses vague/non-specific language',
                    score_impact=1,
                    evidence=f'Contains "{word}"'
                )
                signals.append(signal)
                score += signal.score_impact
        
        # SIGNAL 4: Question instead of answer
        if self._is_question(text, language) and is_comprehension_question:
            signal = ConfusionSignal(
                signal_type='question_response',
                description='Responds with question instead of answer',
                score_impact=2,
                evidence='Ends with question mark or question word'
            )
            signals.append(signal)
            score += signal.score_impact
        
        # SIGNAL 5: Low audio confidence (from Whisper)
        if audio_confidence is not None and audio_confidence < 0.7:
            signal = ConfusionSignal(
                signal_type='low_confidence',
                description='Low speech recognition confidence',
                score_impact=1,
                evidence=f'Confidence: {audio_confidence:.2f}'
            )
            signals.append(signal)
            score += signal.score_impact
        
        # SIGNAL 6: High filler word ratio
        filler_count = len(vague_found)
        if word_count > 0 and (filler_count / word_count) > 0.3:
            signal = ConfusionSignal(
                signal_type='high_filler_ratio',
                description='Excessive filler words',
                score_impact=1,
                evidence=f'{filler_count}/{word_count} words are fillers'
            )
            signals.append(signal)
            score += signal.score_impact
        
        # Determine if confused
        confused = score >= self.confusion_threshold
        confidence_score = min(score / 6.0, 1.0)  # Normalize to 0-1
        
        return {
            'confused': confused,
            'confidence': confidence_score,
            'score': score,
            'threshold': self.confusion_threshold,
            'signals': [
                {
                    'type': s.signal_type,
                    'description': s.description,
                    'impact': s.score_impact,
                    'evidence': s.evidence
                }
                for s in signals
            ],
            'word_count': word_count,
            'is_comprehension_question': is_comprehension_question
        }
    
    def _find_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Find which patterns appear in text"""
        found = []
        for pattern in patterns:
            if pattern in text:
                found.append(pattern)
        return found
    
    def _is_question(self, text: str, language: str) -> bool:
        """Detect if text is a question"""
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words at start
        question_words = {
            'en': ['what', 'why', 'how', 'when', 'where', 'who', 'is', 'are', 'do', 'does', 'can', 'could', 'should'],
            'es': ['qué', 'por qué', 'cómo', 'cuándo', 'dónde', 'quién', 'es', 'son', 'puede', 'debería'],
            'it': ['cosa', 'perché', 'come', 'quando', 'dove', 'chi', 'è', 'sono', 'può', 'dovrebbe']
        }
        
        words = text.split()
        if words and words[0] in question_words.get(language, []):
            return True
        
        return False
    
    def get_confusion_summary(self, analysis: Dict) -> str:
        """Generate human-readable summary of confusion analysis"""
        if not analysis['confused']:
            return "✅ Response shows clear understanding"
        
        summary_parts = [
            f"⚠️ Confusion detected (score: {analysis['score']}/{analysis['threshold']})"
        ]
        
        for signal in analysis['signals']:
            summary_parts.append(f"  - {signal['description']}: {signal['evidence']}")
        
        return "\n".join(summary_parts)


def test_confusion_detector():
    """Test confusion detection with various scenarios"""
    detector = ConfusionDetector()
    
    print("\n" + "="*60)
    print("CONFUSION DETECTOR TEST")
    print("="*60)
    
    # Test 1: Clear response (no confusion)
    print("\n" + "="*60)
    print("Test 1: Clear Response (English)")
    print("="*60)
    response = "The liquid cleans my colon so the doctor can see clearly during the examination"
    result = detector.detect_confusion(response, 'en', is_comprehension_question=True)
    print(f"Response: {response}")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    # Test 2: Confused response (short + vague)
    print("\n" + "="*60)
    print("Test 2: Confused Response (English)")
    print("="*60)
    response = "Um... to clean... something?"
    result = detector.detect_confusion(response, 'en', is_comprehension_question=True)
    print(f"Response: {response}")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    # Test 3: Uncertain response (Spanish)
    print("\n" + "="*60)
    print("Test 3: Uncertain Response (Spanish)")
    print("="*60)
    response = "Creo que... tal vez para limpiar algo?"
    result = detector.detect_confusion(response, 'es', is_comprehension_question=True)
    print(f"Response: {response}")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    # Test 4: Question as response
    print("\n" + "="*60)
    print("Test 4: Question Response (English)")
    print("="*60)
    response = "Is it to clean the intestine?"
    result = detector.detect_confusion(response, 'en', is_comprehension_question=True)
    print(f"Response: {response}")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    # Test 5: Low confidence audio
    print("\n" + "="*60)
    print("Test 5: Low Audio Confidence")
    print("="*60)
    response = "I think maybe something about cleaning"
    result = detector.detect_confusion(
        response, 
        'en', 
        audio_confidence=0.6,
        is_comprehension_question=True
    )
    print(f"Response: {response}")
    print(f"Audio Confidence: 0.6")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    # Test 6: Italian confused
    print("\n" + "="*60)
    print("Test 6: Confused Response (Italian)")
    print("="*60)
    response = "Uhm... forse qualcosa... non so"
    result = detector.detect_confusion(response, 'it', is_comprehension_question=True)
    print(f"Response: {response}")
    print(f"Confused: {result['confused']}")
    print(f"Score: {result['score']}")
    print(detector.get_confusion_summary(result))
    
    print("\n" + "="*60)
    print("✅ Confusion detector tests complete")
    print("="*60)


if __name__ == "__main__":
    test_confusion_detector()
