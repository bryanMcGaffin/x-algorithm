# X Algorithm Analysis Agents

A suite of Python agents that analyze posting volumes against the X (Twitter) recommendation algorithm to find optimal growth strategies.

## Overview

These agents are built on the actual X algorithm codebase, extracting and modeling:

- **Author Diversity Scorer** (`author_diversity_scorer.rs`) - Penalizes multiple posts from same author
- **Weighted Scorer** (`weighted_scorer.rs`) - Combines 19 engagement signals into final score
- **OON Scorer** (`oon_scorer.rs`) - Prioritizes in-network content
- **Age Filter** (`age_filter.rs`) - Filters posts older than threshold
- **Phoenix Model** (`recsys_model.py`) - ML-based ranking using user engagement history

## Agents

### 1. Algorithm Model (`algorithm_model.py`)

Core simulation of X algorithm components:

```python
from algorithm_model import AlgorithmParams, AuthorDiversityModel

params = AlgorithmParams()
diversity = AuthorDiversityModel(params)

# See diminishing returns for posts/day
table = diversity.get_diminishing_returns_table(8)
# Output: [(1, 1.0, 1.0), (2, 1.7, 0.7), (3, 2.29, 0.59), ...]
```

**Key Findings:**
- Posts 1-3: High marginal value (>50%)
- Posts 4-5: Moderate marginal value (30-50%)
- Posts 6+: Low marginal value (<30%)

### 2. Volume Analyst (`volume_analyst.py`)

Compares suggested posting schedules against algorithm constraints:

```python
from volume_analyst import VolumeAnalystAgent, PostingSchedule

agent = VolumeAnalystAgent()

schedule = PostingSchedule(
    posts_per_day=4,
    threads_per_week=3,
    videos_per_week=3,
    long_videos_per_week=2,
    hours_between_posts=4,
    engagement_hours_per_day=1.0,
)

analysis = agent.analyze_schedule(schedule, "My Schedule")
agent.print_analysis(analysis)
```

**Output includes:**
- Effective posts/day after diversity penalty
- Efficiency ratio
- Estimated impressions and followers
- Calendar days to 10K
- Algorithm alignment score (0-100)
- Warnings and recommendations

### 3. Testing Agent (`testing_agent.py`)

Simulates hundreds of configurations to find patterns:

```python
from testing_agent import TestingAgent

agent = TestingAgent()
configs = agent.generate_focused_grid()  # ~500 configs
results = agent.run_test_suite(configs, num_runs=3)

# Get top performers
fastest = agent.get_top_results("days_to_10k", 10)
efficient = agent.get_top_results("effort_per_follower", 10)
pareto = agent.get_pareto_optimal()
```

**Tests combinations of:**
- Posts per day: 1-8
- Threads per week: 0-5
- Videos per week: 0-5
- Long videos (>45s): 0-4
- Engagement hours: 0.25-2.5
- Post spacing: 2-8 hours

### 4. Optimization Agent (`optimization_agent.py`)

Analyzes results to find theoretical optimal configurations:

```python
from optimization_agent import OptimizationAgent, run_full_optimization

report = run_full_optimization()

print(f"Fastest: {report.fastest_config.days_to_10k} days")
print(f"Optimal posts/day: {report.diversity_sweet_spot}")
print(f"Optimal engagement: {report.engagement_sweet_spot} hours")
```

**Finds 4 optimal configurations:**
1. **Fastest** - Minimizes calendar days
2. **Most Efficient** - Minimizes effort per follower
3. **Balanced** - Optimal time × effort tradeoff
4. **Sustainable** - Maintainable long-term

## Usage

### Quick Start

```bash
cd agents
python run_agents.py --mode optimize
```

### Available Modes

```bash
# Analyze playbook schedules
python run_agents.py --mode analyze

# Run simulation testing
python run_agents.py --mode test

# Find optimal configurations (default)
python run_agents.py --mode optimize

# Run all analyses
python run_agents.py --mode all --target 10000
```

### Custom Analysis

```python
from volume_analyst import VolumeAnalystAgent, PostingSchedule

agent = VolumeAnalystAgent()

# Define custom schedule
my_schedule = PostingSchedule(
    posts_per_day=3,
    threads_per_week=2,
    videos_per_week=2,
    long_videos_per_week=2,
    hours_between_posts=5,
    engagement_hours_per_day=1.0,
)

# Analyze
analysis = agent.analyze_schedule(my_schedule, "My Strategy", target_followers=10000)
agent.print_analysis(analysis)
```

## Key Algorithm Findings

### Author Diversity Penalty

From `author_diversity_scorer.rs`:

```
multiplier(position) = (1 - floor) × decay^position + floor

Position 0 (1st post): 1.00x
Position 1 (2nd post): 0.76x
Position 2 (3rd post): 0.59x
Position 3 (4th post): 0.47x
Position 4 (5th post): 0.39x
```

**Implication:** 3-4 posts/day is optimal. Beyond that, each additional post is <40% effective.

### Time-Gated Constraints

Cannot compress calendar time below ~8-10 weeks because:

1. **Diversity penalty** caps effective posts at 3-4/day
2. **Algorithm learning** needs 2-4 weeks to build author embedding
3. **Compound growth** requires time for follower base to amplify distribution

### Content Type Bonuses

From `weighted_scorer.rs`:

| Content Type | Key Bonus |
|--------------|-----------|
| Threads | 3x dwell time signal |
| Long Videos (>45s) | VQV weight bonus |
| Images | Photo expand signal |

### Engagement Signal Weights

Positive signals (weighted score):
- `follow_author`: 2.0x (highest)
- `retweet`: 1.5x
- `quote`: 1.3x
- `share_via_dm`: 1.3x
- `share`: 1.2x
- `reply`: 1.1x
- `favorite`: 1.0x

Negative signals:
- `report`: -10.0x
- `block_author`: -5.0x
- `mute_author`: -3.0x
- `not_interested`: -1.5x

## Theoretical Optimal Configurations

Based on agent analysis:

### Fastest Growth
- **Posts/day:** 4
- **Threads/week:** 4-5
- **Long videos/week:** 3-4
- **Engagement:** 1.5 hours/day
- **Timeline:** ~60-70 days (8-10 weeks)
- **Total effort:** ~200-250 hours

### Most Efficient
- **Posts/day:** 3
- **Threads/week:** 2
- **Long videos/week:** 2
- **Engagement:** 0.75 hours/day
- **Timeline:** ~90-100 days (13-14 weeks)
- **Total effort:** ~150 hours

### Balanced (Recommended)
- **Posts/day:** 3-4
- **Threads/week:** 3
- **Long videos/week:** 2-3
- **Engagement:** 1.0 hours/day
- **Timeline:** ~75-85 days (11-12 weeks)
- **Total effort:** ~180 hours

### Sustainable
- **Posts/day:** 2-3
- **Threads/week:** 2
- **Long videos/week:** 1-2
- **Engagement:** 0.5-0.75 hours/day
- **Timeline:** ~100-120 days (14-17 weeks)
- **Total effort:** ~120-150 hours
- **Daily commitment:** ~1.5 hours

## File Structure

```
agents/
├── README.md                 # This file
├── algorithm_model.py        # Core algorithm simulation
├── volume_analyst.py         # Schedule analysis agent
├── testing_agent.py          # Configuration testing agent
├── optimization_agent.py     # Optimization analysis agent
└── run_agents.py            # Unified runner
```

## Dependencies

- Python 3.8+
- No external packages required (uses only standard library)

## Notes

- Algorithm parameters are estimated from code analysis (actual values redacted in source)
- Simulations include stochastic elements (viral probability) - run multiple times for averaging
- Results are theoretical optimums - actual performance depends on content quality and niche
