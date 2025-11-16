# Battle Story Mode Documentation

## Overview

The Battle Story Mode feature transforms raw battle events into engaging, AI-powered narratives that capture the drama, heroism, and memorable moments of combat. This system automatically generates story summaries at configurable intervals, creating shareable battle reports that bring the simulation to life.

## Features

### AI-Powered Story Generation
- **Multiple Narrative Tones**: Choose from dramatic, heroic, comedic, serious, or documentary styles
- **Automatic Summarization**: Stories generated at configurable intervals (default: 5 minutes)
- **Fallback Mode**: Works without AI API - generates structured summaries from battle metrics
- **Rich Context**: Incorporates battle statistics, key moments, and dramatic events

### Story Metrics
The system tracks and analyzes:
- **Combat Statistics**: Total attacks, critical hits, damage dealt, casualties
- **Lifecycle Events**: Births, deaths, resource collection
- **Dramatic Moments**: Comebacks, betrayals, last stands, alliances
- **Key Highlights**: Notable events and turning points

### Export & Sharing
- **Text Format**: Export as `.txt` files
- **Markdown Format**: Export as `.md` with formatting
- **Batch Export**: Save all generated stories at once
- **Directory Organization**: Automatically organized story archives

### Interactive UI
- **Story Viewer Panel**: Dedicated UI component with scrollable text display
- **Tone Selection**: Change narrative style and regenerate stories on the fly
- **Live Access**: View stories at any time during battle (press 'S')
- **Smooth Scrolling**: Mouse wheel and keyboard navigation

## Quick Start

### Basic Usage

```python
from src.systems.battle_story_summarizer import (
    BattleStoryGenerator, BattleStoryTracker, StoryTone
)

# Initialize story generator
generator = BattleStoryGenerator(default_tone=StoryTone.DRAMATIC)

# Create tracker for automatic generation (every 5 minutes)
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=300.0  # 5 minutes
)

# Start collecting events
tracker.start_tracking()

# Add battle events as they occur
def on_battle_event(event):
    tracker.generator.add_event(event)

battle.add_event_callback(on_battle_event)

# Check if it's time to generate a story
if tracker.should_generate_story():
    story = tracker.generate_and_store_story()
    print(story)

# Export all stories
tracker.export_all_stories('battle_stories', format='txt')
```

### With UI Integration

```python
from src.rendering import StoryViewer, StoryViewerAction

# Create story viewer
viewer = StoryViewer(width=700, height=600)

# Set story content
viewer.set_story(story_text, StoryTone.HEROIC)

# Handle events
result = viewer.handle_event(event, x_offset=350, y_offset=150)
if result:
    action, data = result
    
    if action == StoryViewerAction.CHANGE_TONE:
        new_story = generator.generate_story(tone=data)
        viewer.set_story(new_story, data)
    
    elif action == StoryViewerAction.EXPORT_TXT:
        generator.export_story(story, "my_story.txt", 'txt')

# Draw the viewer
viewer.draw(surface, x=350, y=150)
```

## Running the Demo

The interactive demo showcases all features:

```bash
python3 -m examples.battle_story_mode_demo
```

**Demo Features:**
- Real-time battle visualization
- Automatic story generation every 30 seconds (demo speed)
- Press 'S' to view story panel at any time
- Change tones and regenerate stories interactively
- Export stories with one click
- Notifications when new stories are available

**Controls:**
- `SPACE`: Pause/Resume battle
- `S`: Toggle story viewer
- `ESC`: Close story viewer / Pause menu
- Mouse Wheel / Arrow Keys: Scroll story text

## Story Tones

### Dramatic (Default)
Creates tension-filled narratives with emotional weight and dramatic tension:
> "In the shadow of the ancient arena, warriors clashed with desperate fury. Aragorn's blade sang through the air as Saruman's dark forces pressed their advantage. When all seemed lost, a critical strike turned the tide..."

### Heroic
Epic tales celebrating bravery, valor, and legendary feats:
> "From the halls of legend comes this tale of valor! The brave Aragorn stood tall against impossible odds, his courage inspiring allies to heights of glory. With mighty blows and unwavering spirit..."

### Comedic
Lighthearted accounts finding humor in the chaos:
> "Well, that escalated quickly! Gandalf attempted a dramatic entrance but tripped over a pellet. Meanwhile, Pippin discovered that aggressive charging works better when you pick a target first..."

### Serious
Gritty, realistic battle reports:
> "Engagement commenced at 14:30. Casualties mounted as aggressive tactics from Team Broans met staunch defense. Kill ratio 3:2. Resource depletion critical by minute 4..."

### Documentary
Analytical, nature documentary style:
> "Here in the digital arena, we observe the fascinating behavior of the warrior species. Note how the aggressive phenotype dominates early exchanges, while cautious variants employ evasion tactics..."

## Configuration

### Story Generation Timing

```python
# Quick stories (for demos/testing)
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=30.0  # 30 seconds
)

# Standard interval
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=300.0  # 5 minutes
)

# Extended battles
tracker = BattleStoryTracker(
    generator=generator,
    story_interval_seconds=600.0  # 10 minutes
)
```

### AI Model Selection

```python
# Use different OpenAI models
generator = BattleStoryGenerator(
    model="gpt-4o",  # More creative, higher quality
    default_tone=StoryTone.HEROIC
)

generator = BattleStoryGenerator(
    model="gpt-4o-mini",  # Faster, more cost-effective (default)
    default_tone=StoryTone.DRAMATIC
)
```

### API Key Configuration

Set your OpenAI API key via environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Or pass it directly:

```python
generator = BattleStoryGenerator(
    api_key="sk-...",
    model="gpt-4o-mini"
)
```

**Note**: If no API key is provided, the system automatically falls back to metric-based story generation.

## Architecture

### BattleStoryGenerator
Core story generation engine:
- Collects battle events and logs
- Extracts metrics and statistics
- Generates AI prompts based on tone
- Produces fallback stories when API unavailable
- Handles export functionality

### BattleStoryTracker
Manages automatic story generation:
- Tracks time intervals
- Triggers story generation
- Stores story history
- Batch export functionality

### StoryViewer
Pygame UI component:
- Displays formatted stories
- Handles user interaction
- Tone selection interface
- Export controls
- Scroll management

## Integration with Battle System

The story system integrates seamlessly with the existing battle infrastructure:

```python
# Create battle with living world features
battle = SpatialBattle(
    creatures,
    arena_width=120.0,
    arena_height=90.0,
    living_world_enhancer=living_world
)

# Set up story tracking
tracker.start_tracking()

# Connect event callback
battle.add_event_callback(lambda event: tracker.generator.add_event(event))

# Also collect text logs
for log in battle.get_battle_log():
    tracker.generator.add_log(log)

# In game loop
if tracker.should_generate_story():
    story = tracker.generate_and_store_story()
    viewer.set_story(story, current_tone)
```

## Example Story Output

```
⚡ BATTLE STORY ⚡

In a fierce arena clash spanning three intense minutes, ten warriors 
entered but only five would emerge victorious. The battle opened with 
Aragorn and Gimli leading an aggressive charge, their coordinated strikes 
overwhelming the cautious Frodo early on.

The tide turned when Gandalf executed a masterful comeback, recovering 
from near-death with only 8% health to strike down Saruman in a critical 
blow. This stunning reversal emboldened the Alliance, leading to a series 
of dramatic confrontations.

Notable moments included Sam's surprising betrayal of his longtime ally 
Merry, and Legolas's precision strikes that earned him MVP status with 
247 damage dealt across 18 attacks. The arena saw 11 casualties, 3 births, 
and countless narrow escapes as warriors scrambled for the 23 resources 
scattered across the battlefield.

In the end, the survivors—bloodied but unbroken—stood among the ruins, 
their stories forever etched in arena legend.

---
Battle Duration: 3.2 minutes | Attacks: 67 | Casualties: 11 | Births: 3
```

## API Reference

### BattleStoryGenerator

```python
BattleStoryGenerator(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    default_tone: StoryTone = StoryTone.DRAMATIC
)
```

**Methods:**
- `start_collection()`: Begin collecting events
- `add_event(event)`: Add a battle event
- `add_log(message)`: Add a log message
- `generate_story(tone, max_tokens)`: Generate story
- `export_story(story, filepath, format)`: Export to file

### BattleStoryTracker

```python
BattleStoryTracker(
    generator: BattleStoryGenerator,
    story_interval_seconds: float = 300.0
)
```

**Methods:**
- `start_tracking()`: Begin tracking
- `stop_tracking()`: Stop tracking
- `should_generate_story()`: Check if interval elapsed
- `generate_and_store_story(tone)`: Generate and save story
- `get_all_stories()`: Get story history
- `export_all_stories(directory, format)`: Batch export

### StoryViewer

```python
StoryViewer(
    width: int = 600,
    height: int = 500,
    font_size: int = 18
)
```

**Methods:**
- `set_story(story, tone)`: Update displayed story
- `handle_event(event, x_offset, y_offset)`: Process events
- `draw(surface, x, y)`: Render viewer

## Best Practices

1. **Set Appropriate Intervals**: Use longer intervals (5-10 minutes) for production, shorter for demos
2. **Monitor API Costs**: Use `gpt-4o-mini` for cost-effectiveness
3. **Test Fallback Mode**: Ensure your game works without API access
4. **Export Regularly**: Save stories to disk for player sharing
5. **Vary Tones**: Offer players tone selection for replay value
6. **Integrate with Living World**: Richer creature histories = better stories

## Troubleshooting

### No AI Stories Generated
- Check `OPENAI_API_KEY` environment variable
- Verify API key has credits
- Check console for error messages
- Fallback mode should still work

### Story Too Short/Long
- Adjust `max_tokens` parameter in `generate_story()`
- Default is 500 tokens (~350 words)

### Export Fails
- Check write permissions for export directory
- Verify directory exists or can be created
- Check disk space

## Future Enhancements

Planned features for future releases:
- [ ] Integration with Discord webhooks
- [ ] Image generation for key moments
- [ ] Multi-story compilation for long battles
- [ ] Player-facing story gallery UI
- [ ] Voice narration option
- [ ] Community story sharing platform

## Performance Notes

- Story generation is async-friendly (API calls can be non-blocking)
- Fallback mode is instant (no API latency)
- Metrics extraction is lightweight (< 1ms typically)
- UI rendering is optimized for 60 FPS

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest tests.test_battle_story_summarizer -v
```

**Test Coverage:**
- Event collection and metric tracking
- Story generation with all tones
- Export functionality (TXT and MD)
- Tracker timing and interval logic
- Story storage and retrieval
- All 20 tests passing ✓

## Support

For issues, feature requests, or questions:
- Check existing documentation
- Review example code in `examples/battle_story_mode_demo.py`
- Run tests to verify functionality
- Check console output for error messages
