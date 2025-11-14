# Evolution Battle Game

## Project Description
This is an evolution-based battle game where players can engage in battles, breed their fighters, and place bets.

## Current Status
✅ **Core Gameplay Implementation Complete!**

The game now includes a fully functional CLI-based demonstration with:
- **Fighter System**: Fighters with inheritable traits and power calculations
- **Battle System**: Simulated battles with power-based outcomes and randomization
- **Betting System**: Place bets on fighters and calculate payouts
- **Breeding System**: Create offspring with inherited traits and mutations
- **Working Demo**: Run `python main.py` to see the full gameplay cycle

## Quick Start
```bash
# Clone the repository
git clone https://github.com/dbmelville2-jpg/evobattle
cd evobattle

# Install dependencies
pip install -r requirements.txt

# Run the demo
python main.py
```

The demo showcases:
1. Generating random fighters with unique traits
2. Simulating battles between fighters
3. Placing bets and calculating payouts
4. Breeding winners to create next generation fighters
5. Tracking battle history and fighter lineages

## Project Architecture

### Implemented Components
- **Models** (`src/models/`)
  - `Fighter`: Represents a battle-ready fighter with traits, stats, and lineage
  - `Trait`: Inheritable characteristics that affect fighter power
  - `Lineage`: Tracks ancestry and breeding history

- **Systems** (`src/systems/`)
  - `BattleSystem`: Manages combat and determines winners
  - `BettingSystem`: Handles wagers and payouts
  - `BreedingSystem`: Creates offspring with trait inheritance and mutations

- **Utilities** (`src/utils/`)
  - `RandomGenerator`: Creates random fighters, traits, and names

## For Developers

### Agent Coordination
This project is developed by three specialist agents working in coordination:
- **Core Gameplay Engineer** - Implements game mechanics, physics, and player interaction ([Issue #11](https://github.com/dbmelville2-jpg/evobattle/issues/11)) ✅ **CLI Implementation Complete**
- **Graphics & Rendering Agent** - Handles visual systems, animations, and UI ([Issue #12](https://github.com/dbmelville2-jpg/evobattle/issues/12)) 🔄 **Future Enhancement**
- **Data & Systems Agent** - Manages game state, persistence, and support systems ([Issue #13](https://github.com/dbmelville2-jpg/evobattle/issues/13)) 🔄 **Future Enhancement**

**Important Documentation:**
- [Agent Coordination Guide](AGENT_COORDINATION.md) - Team standards, interface contracts, and integration goals
- [Integration Checklist](INTEGRATION_CHECKLIST.md) - Track implementation progress and integration milestones
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [Project Architect Vision](https://github.com/dbmelville2-jpg/evobattle/issues/2) - Overall project leadership and vision

## Future Enhancements
As noted in the demo output, potential next steps include:
- Web interface for interactive gameplay
- Persistent storage for fighter lineages
- Advanced trait combinations and synergies
- Tournament brackets
- Player accounts and leaderboards
- Graphics and rendering system
- Save/load functionality