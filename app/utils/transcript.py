"""Bilingual transcript manager for consent conversations"""

from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

class TranscriptManager:
    """Manages bilingual transcripts for consent verification sessions"""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize transcript manager
        
        Args:
            session_id: Optional session ID (auto-generated if None)
        """
        self.session_id = session_id or self._generate_session_id()
        self.entries = []
        self.metadata = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'language': None,
            'procedure': None,
            'patient_id': None  # Can be added for compliance
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"CS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def add_entry(
        self,
        speaker: str,
        text_original: str,
        text_translation: Optional[str] = None,
        language: str = 'en',
        flags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add entry to transcript
        
        Args:
            speaker: 'PATIENT' or 'SYSTEM'
            text_original: Original text in spoken language
            text_translation: English translation (if different from original)
            language: Language code (en, es, it)
            flags: Optional flags (e.g., 'confusion_detected', 'needs_review')
            metadata: Optional additional metadata (latency, confidence, etc.)
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'speaker': speaker,
            'text_original': text_original,
            'text_translation': text_translation or text_original,
            'language': language,
            'flags': flags or [],
            'metadata': metadata or {}
        }
        
        self.entries.append(entry)
    
    def set_metadata(
        self,
        language: str = None,
        procedure: str = None,
        patient_id: str = None
    ):
        """Update session metadata"""
        if language:
            self.metadata['language'] = language
        if procedure:
            self.metadata['procedure'] = procedure
        if patient_id:
            self.metadata['patient_id'] = patient_id
    
    def get_formatted_transcript(self) -> str:
        """
        Get formatted bilingual transcript for display/printing
        
        Returns:
            Formatted string with bilingual transcript
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"CONSENT VERIFICATION SESSION: {self.session_id}")
        lines.append("=" * 80)
        lines.append(f"Language: {self.metadata.get('language', 'Unknown')}")
        lines.append(f"Procedure: {self.metadata.get('procedure', 'Unknown')}")
        lines.append(f"Started: {self.metadata['started_at']}")
        if self.metadata.get('patient_id'):
            lines.append(f"Patient ID: {self.metadata['patient_id']}")
        lines.append("=" * 80)
        lines.append("")
        
        for entry in self.entries:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            speaker = entry['speaker']
            lang = entry['language'].upper()
            
            # Original language
            lines.append(f"[{timestamp}] {speaker} ({lang}):")
            lines.append(f"  {entry['text_original']}")
            
            # Translation (if different)
            if entry['text_original'] != entry['text_translation']:
                lines.append(f"  [EN]: {entry['text_translation']}")
            
            # Flags
            if entry['flags']:
                flags_str = ', '.join(entry['flags'])
                lines.append(f"  ⚠️  Flags: {flags_str}")
            
            # Metadata (latency, confidence, etc.)
            if entry['metadata']:
                meta_items = []
                if 'latency_ms' in entry['metadata']:
                    meta_items.append(f"latency: {entry['metadata']['latency_ms']:.0f}ms")
                if 'confidence' in entry['metadata']:
                    meta_items.append(f"confidence: {entry['metadata']['confidence']:.2f}")
                if meta_items:
                    lines.append(f"  📊 {', '.join(meta_items)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def get_dual_column_transcript(self) -> Dict:
        """
        Get transcript formatted for dual-column display
        
        Returns:
            Dict with original and translation columns
        """
        original_column = []
        translation_column = []
        
        for entry in self.entries:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            speaker = entry['speaker']
            
            # Original column
            original_entry = {
                'timestamp': timestamp,
                'speaker': speaker,
                'language': entry['language'],
                'text': entry['text_original'],
                'flags': entry['flags']
            }
            original_column.append(original_entry)
            
            # Translation column
            translation_entry = {
                'timestamp': timestamp,
                'speaker': speaker,
                'language': 'en',
                'text': entry['text_translation'],
                'flags': entry['flags']
            }
            translation_column.append(translation_entry)
        
        return {
            'session_id': self.session_id,
            'metadata': self.metadata,
            'original': original_column,
            'translation': translation_column
        }
    
    def export_json(self, output_path: str):
        """
        Export transcript as JSON
        
        Args:
            output_path: Path to save JSON file
        """
        data = {
            'session_id': self.session_id,
            'metadata': self.metadata,
            'entries': self.entries
        }
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Transcript exported to {output_path}")
    
    def get_statistics(self) -> Dict:
        """
        Get transcript statistics
        
        Returns:
            Dict with session statistics
        """
        total_entries = len(self.entries)
        patient_entries = sum(1 for e in self.entries if e['speaker'] == 'PATIENT')
        system_entries = sum(1 for e in self.entries if e['speaker'] == 'SYSTEM')
        
        flagged_entries = sum(1 for e in self.entries if e['flags'])
        
        # Calculate duration
        if self.entries:
            start_time = datetime.fromisoformat(self.entries[0]['timestamp'])
            end_time = datetime.fromisoformat(self.entries[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds()
        else:
            duration = 0
        
        # Count unique flags
        all_flags = []
        for entry in self.entries:
            all_flags.extend(entry['flags'])
        unique_flags = set(all_flags)
        
        return {
            'session_id': self.session_id,
            'total_entries': total_entries,
            'patient_entries': patient_entries,
            'system_entries': system_entries,
            'flagged_entries': flagged_entries,
            'unique_flags': list(unique_flags),
            'duration_seconds': duration,
            'language': self.metadata.get('language'),
            'procedure': self.metadata.get('procedure')
        }
    
    def get_clinical_summary(self) -> Dict:
        """
        Get clinical summary for review
        
        Returns:
            Dict with entries needing clinical review
        """
        flagged = [e for e in self.entries if e['flags']]
        
        confusion_detected = [
            e for e in self.entries
            if 'confusion_detected' in e['flags']
        ]
        
        needs_review = [
            e for e in self.entries
            if 'needs_review' in e['flags'] or 'translation_uncertain' in e['flags']
        ]
        
        return {
            'total_flagged': len(flagged),
            'confusion_detected': len(confusion_detected),
            'needs_review': len(needs_review),
            'flagged_entries': flagged
        }

def test_transcript():
    """Test transcript manager"""
    print("\n" + "="*60)
    print("Transcript Manager Test")
    print("="*60)
    
    # Create test transcript
    transcript = TranscriptManager()
    transcript.set_metadata(
        language='es',
        procedure='colonoscopy',
        patient_id='TEST-001'
    )
    
    print(f"Session ID: {transcript.session_id}")
    
    # Add entries
    transcript.add_entry(
        speaker='SYSTEM',
        text_original='Buenos días. Estoy aquí para ayudarle con su procedimiento.',
        text_translation='Good morning. I am here to help you with your procedure.',
        language='es',
        metadata={'latency_ms': 2845, 'tts_latency_ms': 320}
    )
    
    transcript.add_entry(
        speaker='PATIENT',
        text_original='¿Es doloroso?',
        text_translation='Is it painful?',
        language='es',
        metadata={'confidence': 0.98, 'latency_ms': 450}
    )
    
    transcript.add_entry(
        speaker='SYSTEM',
        text_original='No, el procedimiento se hace bajo anestesia.',
        text_translation='No, the procedure is done under anesthesia.',
        language='es',
        metadata={'latency_ms': 2912}
    )
    
    transcript.add_entry(
        speaker='PATIENT',
        text_original='Um... para limpiar... algo?',
        text_translation='Um... to clean... something?',
        language='es',
        flags=['confusion_detected', 'vague_response', 'needs_review'],
        metadata={'confidence': 0.72}
    )
    
    # Print formatted transcript
    print("\n" + "="*60)
    print("FORMATTED TRANSCRIPT")
    print("="*60)
    print(transcript.get_formatted_transcript())
    
    # Print statistics
    print("\n" + "="*60)
    print("SESSION STATISTICS")
    print("="*60)
    stats = transcript.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Print clinical summary
    print("\n" + "="*60)
    print("CLINICAL SUMMARY")
    print("="*60)
    summary = transcript.get_clinical_summary()
    print(f"  Total flagged: {summary['total_flagged']}")
    print(f"  Confusion detected: {summary['confusion_detected']}")
    print(f"  Needs review: {summary['needs_review']}")
    
    # Export to JSON
    export_path = 'data/sessions/test_transcript.json'
    transcript.export_json(export_path)
    
    # Test dual column format
    print("\n" + "="*60)
    print("DUAL COLUMN FORMAT (JSON)")
    print("="*60)
    dual = transcript.get_dual_column_transcript()
    print(json.dumps(dual, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n✅ Transcript manager ready")

if __name__ == "__main__":
    test_transcript()
