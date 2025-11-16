"""
Battle Story Summarizer - AI-powered battle narrative generation.

This module uses AI to generate engaging story summaries from battle logs,
capturing key events, MVP creatures, alliances, betrayals, and dramatic moments.
"""

from typing import List, Optional, Dict, Any
import time
from enum import Enum
from dataclasses import dataclass, field
import os

# Optional OpenAI import - system works without it but won't generate AI stories
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class StoryTone(Enum):
    """Narrative tone options for story generation."""
    SERIOUS = "serious"
    HEROIC = "heroic"
    COMEDIC = "comedic"
    DRAMATIC = "dramatic"
    DOCUMENTARY = "documentary"


@dataclass
class BattleStoryMetrics:
    """Metrics and statistics extracted from battle events."""
    duration_seconds: float = 0.0
    total_attacks: int = 0
    total_kills: int = 0
    total_births: int = 0
    total_damage_dealt: float = 0.0
    critical_hits: int = 0
    creatures_started: int = 0
    creatures_survived: int = 0
    resource_collections: int = 0
    key_moments: List[str] = field(default_factory=list)
    mvp_creatures: List[Dict[str, Any]] = field(default_factory=list)
    dramatic_events: List[str] = field(default_factory=list)


class BattleStoryGenerator:
    """
    Generates AI-powered story summaries from battle events and logs.
    
    Collects battle events over a time window and produces engaging narratives
    highlighting key moments, heroes, villains, and turning points.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        default_tone: StoryTone = StoryTone.DRAMATIC
    ):
        """
        Initialize the battle story generator.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use for generation
            default_tone: Default narrative tone
        """
        self.default_tone = default_tone
        self.model = model
        
        # Initialize OpenAI client if available
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        # Event collection
        self.collected_events: List[Any] = []
        self.battle_logs: List[str] = []
        self.start_time: Optional[float] = None
        self.metrics = BattleStoryMetrics()
    
    def start_collection(self):
        """Start collecting battle events for story generation."""
        self.collected_events = []
        self.battle_logs = []
        self.start_time = time.time()
        self.metrics = BattleStoryMetrics()
    
    def add_event(self, event: Any):
        """Add a battle event to the collection."""
        self.collected_events.append(event)
        
        # Update metrics based on event type
        if hasattr(event, 'event_type'):
            event_type = str(event.event_type.value) if hasattr(event.event_type, 'value') else str(event.event_type)
            
            if event_type == 'ability_use':
                self.metrics.total_attacks += 1
            elif event_type == 'damage_dealt':
                if hasattr(event, 'value') and event.value:
                    self.metrics.total_damage_dealt += event.value
            elif event_type == 'critical_hit':
                self.metrics.critical_hits += 1
            elif event_type in ['creature_death', 'creature_faint']:
                self.metrics.total_kills += 1
                if hasattr(event, 'message'):
                    self.metrics.dramatic_events.append(event.message)
            elif event_type == 'creature_birth':
                self.metrics.total_births += 1
                if hasattr(event, 'message'):
                    self.metrics.key_moments.append(event.message)
            elif event_type == 'resource_collected':
                self.metrics.resource_collections += 1
    
    def add_log(self, log_message: str):
        """Add a battle log message to the collection."""
        self.battle_logs.append(log_message)
    
    def _extract_metrics_from_logs(self) -> BattleStoryMetrics:
        """Extract additional metrics from battle logs."""
        # Update duration if we have a start time
        if self.start_time:
            self.metrics.duration_seconds = time.time() - self.start_time
        
        # Analyze logs for additional patterns
        for log in self.battle_logs:
            log_lower = log.lower()
            
            # Detect dramatic moments
            if any(word in log_lower for word in ['comeback', 'reversal', 'betrayal', 'alliance']):
                self.metrics.key_moments.append(log)
            
            # Detect survival/last stand moments
            if 'survivor' in log_lower or 'last stand' in log_lower:
                self.metrics.dramatic_events.append(log)
        
        return self.metrics
    
    def _build_fallback_story(self, tone: StoryTone) -> str:
        """Build a basic story without AI when API is unavailable."""
        metrics = self._extract_metrics_from_logs()
        
        # Build story based on metrics
        story_lines = []
        
        # Title
        if tone == StoryTone.HEROIC:
            story_lines.append("⚔️ EPIC BATTLE CHRONICLE ⚔️\n")
        elif tone == StoryTone.COMEDIC:
            story_lines.append("🎭 THE RIDICULOUS ARENA TALES 🎭\n")
        elif tone == StoryTone.DOCUMENTARY:
            story_lines.append("📊 BATTLE ANALYSIS REPORT 📊\n")
        else:
            story_lines.append("⚡ BATTLE STORY ⚡\n")
        
        # Duration
        duration_min = int(metrics.duration_seconds // 60)
        duration_sec = int(metrics.duration_seconds % 60)
        story_lines.append(f"Duration: {duration_min}m {duration_sec}s\n")
        
        # Statistics
        story_lines.append(f"\n📈 Battle Statistics:")
        story_lines.append(f"  • Total Attacks: {metrics.total_attacks}")
        story_lines.append(f"  • Critical Hits: {metrics.critical_hits}")
        story_lines.append(f"  • Total Damage: {metrics.total_damage_dealt:.1f}")
        story_lines.append(f"  • Casualties: {metrics.total_kills}")
        story_lines.append(f"  • Births: {metrics.total_births}")
        story_lines.append(f"  • Resources Collected: {metrics.resource_collections}")
        
        # Key moments
        if metrics.key_moments:
            story_lines.append(f"\n🌟 Key Moments:")
            for moment in metrics.key_moments[:5]:
                story_lines.append(f"  • {moment}")
        
        # Dramatic events
        if metrics.dramatic_events:
            story_lines.append(f"\n💥 Dramatic Events:")
            for event in metrics.dramatic_events[:5]:
                story_lines.append(f"  • {event}")
        
        # Sample battle logs
        if self.battle_logs:
            story_lines.append(f"\n📜 Battle Log Highlights (last 10 events):")
            for log in self.battle_logs[-10:]:
                story_lines.append(f"  {log}")
        
        return "\n".join(story_lines)
    
    def _build_ai_prompt(self, tone: StoryTone) -> str:
        """Build the AI prompt for story generation."""
        metrics = self._extract_metrics_from_logs()
        
        # Tone-specific instructions
        tone_instructions = {
            StoryTone.SERIOUS: "Write a serious, gritty battle report that captures the brutal reality of combat.",
            StoryTone.HEROIC: "Write an epic, heroic tale celebrating bravery, valor, and legendary feats.",
            StoryTone.COMEDIC: "Write a humorous, lighthearted account that finds comedy in the chaos.",
            StoryTone.DRAMATIC: "Write a dramatic narrative with tension, twists, and emotional weight.",
            StoryTone.DOCUMENTARY: "Write a factual, analytical report in the style of a nature documentary."
        }
        
        prompt = f"""You are a master storyteller tasked with creating an engaging battle narrative.

{tone_instructions.get(tone, tone_instructions[StoryTone.DRAMATIC])}

Battle Statistics:
- Duration: {metrics.duration_seconds:.0f} seconds ({metrics.duration_seconds/60:.1f} minutes)
- Total Attacks: {metrics.total_attacks}
- Critical Hits: {metrics.critical_hits}
- Total Damage Dealt: {metrics.total_damage_dealt:.1f}
- Casualties: {metrics.total_kills}
- New Births: {metrics.total_births}
- Resources Collected: {metrics.resource_collections}

Key Moments:
{chr(10).join(f'- {moment}' for moment in metrics.key_moments[:10]) if metrics.key_moments else '(None recorded)'}

Dramatic Events:
{chr(10).join(f'- {event}' for event in metrics.dramatic_events[:10]) if metrics.dramatic_events else '(None recorded)'}

Recent Battle Log (last 30 entries):
{chr(10).join(self.battle_logs[-30:]) if self.battle_logs else '(No logs available)'}

Create a compelling 150-250 word story that:
1. Captures the essence of the battle
2. Highlights MVP creatures and memorable moments
3. Describes turning points and dramatic shifts
4. Mentions notable alliances, betrayals, or rivalries if present
5. Ends with a sense of resolution or anticipation

Keep it engaging, vivid, and match the requested tone. Make readers feel like they witnessed something memorable."""
        
        return prompt
    
    def generate_story(
        self,
        tone: Optional[StoryTone] = None,
        max_tokens: int = 500
    ) -> str:
        """
        Generate an AI-powered story from collected events.
        
        Args:
            tone: Narrative tone (uses default if not specified)
            max_tokens: Maximum tokens for AI generation
            
        Returns:
            Generated story as a string
        """
        tone = tone or self.default_tone
        
        # If OpenAI is not available or not configured, use fallback
        if not self.client:
            return self._build_fallback_story(tone)
        
        try:
            # Build prompt
            prompt = self._build_ai_prompt(tone)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative battle narrator who creates engaging stories from combat logs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.8
            )
            
            # Extract story
            story = response.choices[0].message.content.strip()
            
            # Add metadata footer
            metrics = self._extract_metrics_from_logs()
            footer = f"\n\n---\nBattle Duration: {metrics.duration_seconds/60:.1f} minutes | "
            footer += f"Attacks: {metrics.total_attacks} | "
            footer += f"Casualties: {metrics.total_kills} | "
            footer += f"Births: {metrics.total_births}"
            
            return story + footer
            
        except Exception as e:
            # Fall back to basic story on error
            print(f"AI story generation failed: {e}")
            return self._build_fallback_story(tone)
    
    def export_story(self, story: str, filepath: str, format: str = 'txt'):
        """
        Export story to a file.
        
        Args:
            story: The story text to export
            filepath: Path to save the file
            format: Export format ('txt' or 'md')
        """
        if format == 'md':
            # Add markdown formatting
            story = f"# Battle Story\n\n{story}\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(story)


class BattleStoryTracker:
    """
    Tracks battle progress and triggers story generation at intervals.
    
    Integrates with SpatialBattle to automatically collect events and
    generate stories at configurable time windows.
    """
    
    def __init__(
        self,
        generator: BattleStoryGenerator,
        story_interval_seconds: float = 300.0  # 5 minutes default
    ):
        """
        Initialize the battle story tracker.
        
        Args:
            generator: BattleStoryGenerator instance
            story_interval_seconds: Time between story generations
        """
        self.generator = generator
        self.story_interval = story_interval_seconds
        self.last_story_time: float = 0.0
        self.stories: List[Dict[str, Any]] = []
        self.is_tracking = False
    
    def start_tracking(self):
        """Start tracking battle events."""
        self.is_tracking = True
        self.last_story_time = time.time()
        self.generator.start_collection()
    
    def stop_tracking(self):
        """Stop tracking battle events."""
        self.is_tracking = False
    
    def should_generate_story(self) -> bool:
        """Check if it's time to generate a new story."""
        if not self.is_tracking:
            return False
        
        current_time = time.time()
        elapsed = current_time - self.last_story_time
        return elapsed >= self.story_interval
    
    def generate_and_store_story(self, tone: Optional[StoryTone] = None) -> str:
        """
        Generate a story and store it in the history.
        
        Args:
            tone: Narrative tone for the story
            
        Returns:
            Generated story text
        """
        story = self.generator.generate_story(tone=tone)
        
        self.stories.append({
            'timestamp': time.time(),
            'story': story,
            'tone': tone or self.generator.default_tone,
            'metrics': self.generator.metrics
        })
        
        # Reset for next interval
        self.last_story_time = time.time()
        self.generator.start_collection()
        
        return story
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Get all generated stories."""
        return self.stories
    
    def export_all_stories(self, directory: str, format: str = 'txt'):
        """
        Export all stories to files.
        
        Args:
            directory: Directory to save stories
            format: Export format ('txt' or 'md')
        """
        os.makedirs(directory, exist_ok=True)
        
        for i, story_data in enumerate(self.stories):
            filename = f"battle_story_{i+1}.{format}"
            filepath = os.path.join(directory, filename)
            self.generator.export_story(story_data['story'], filepath, format)
