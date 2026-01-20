# X Growth Playbook: 0 to 10,000 Followers

## Algorithmic Success Blueprint

This playbook maps every action to specific X algorithm components for maximum efficiency. Each step includes the **algorithmic rationale** so you understand exactly why it works.

---

# Phase 1: Strategic Foundation (Days 1-3)

## Step 1.1: Niche Selection for Algorithmic Advantage

### Action
Choose a niche that satisfies ALL of these criteria:

| Criterion | Why It Matters Algorithmically |
|-----------|-------------------------------|
| **High engagement density** | Phoenix retrieval model finds posts via semantic similarity to user history. Dense niches = more potential matches |
| **Active reply culture** | `P(reply)` is a weighted positive signal. Niches with discussions amplify this |
| **Share-friendly content** | `share_score`, `share_via_dm_score`, `share_via_copy_link_score` are separate signals |
| **Video-compatible** | VQV (Video Quality View) weight gives video content algorithmic boost |
| **Monetizable** | Brands/products exist in space for future revenue |

### Recommended Niches (Ranked by Algorithm Fit)
1. **AI/Tech tutorials** - High share rate, video-friendly, premium advertisers
2. **Finance/Investing** - High engagement, share-worthy, monetizable
3. **Fitness transformation** - Visual, video-native, product partnerships
4. **Business/Entrepreneurship** - High reply culture, share-friendly
5. **Creator economy** - Meta-audience of engaged users

### Algorithm Component
```
Phoenix Retrieval Model (two-tower architecture):
- User tower: encodes user + their last 128 engagements
- Candidate tower: encodes post + author
- Match score = dot_product(user_embedding, candidate_embedding)

Niche selection affects: candidate_author_embeddings coherence
```

**Checkpoint**: Write down your chosen niche and 5 specific sub-topics within it.

---

## Step 1.2: Profile Optimization for Follow Conversion

### Action
Optimize every profile element for the `P(follow_author)` signal.

### Profile Photo
- High contrast, clear face or memorable logo
- Stands out at small size in notifications

### Display Name
```
Formula: [Name] + [Value Proposition in 2-3 words]
Examples:
- "Alex Chen | AI Explained"
- "Sarah K. - Wealth Builder"
- "Mike Fitness | Transform"
```

### Bio Structure
```
Line 1: What you do (identity statement)
Line 2: What followers get (value proposition)
Line 3: Credibility marker (social proof)
Line 4: CTA or personality
```

### Algorithm Component
```rust
// From weighted_scorer.rs
+ Self::apply(s.profile_click_score, p::PROFILE_CLICK_WEIGHT)
+ Self::apply(s.follow_author_score, p::FOLLOW_AUTHOR_WEIGHT)
```
Profile clicks that convert to follows generate TWO positive signals on the originating post, training the model to show your content to similar users.

**Checkpoint**: Complete profile with photo, optimized name, and bio.

---

## Step 1.3: Pinned Post Strategy

### Action
Create and pin a post that maximizes `P(follow_author)`.

### Pinned Post Formula
```
Hook: Provocative claim or impressive result
Body: 3-5 bullet points of value you provide
Proof: Specific credential or result
CTA: Clear reason to follow
```

### Example Structure
```
I grew from 0 to 50K followers in 6 months.

Here's exactly what I post about:
→ [Topic 1] - [specific benefit]
→ [Topic 2] - [specific benefit]
→ [Topic 3] - [specific benefit]

I share everything I learn along the way.

Follow along if you want [specific outcome].
```

### Algorithm Component
```
Pinned post is first thing seen after profile_click.
High-converting pinned post → more follows →
more in-network distribution for future posts.
```

**Checkpoint**: Publish and pin your conversion-optimized post.

---

# Phase 2: Content Engine Setup (Days 4-7)

## Step 2.1: Content Pillar Architecture

### Action
Create 3-4 content pillars that each target different engagement signals.

| Pillar Type | Target Signal | Post Frequency |
|-------------|---------------|----------------|
| **Educational threads** | `dwell_time` (continuous) | 2x/week |
| **Hot takes/opinions** | `P(reply)`, `P(quote)` | 3x/week |
| **Visual/Video content** | `VQV_WEIGHT`, `P(photo_expand)` | 2x/week |
| **Shareable insights** | `share_score`, `share_via_dm_score` | 2x/week |

### Algorithm Component
```rust
// Multiple engagement types combine additively
final_score =
    favorite_score * FAVORITE_WEIGHT
    + reply_score * REPLY_WEIGHT
    + retweet_score * RETWEET_WEIGHT
    + quote_score * QUOTE_WEIGHT
    + click_score * CLICK_WEIGHT
    + profile_click_score * PROFILE_CLICK_WEIGHT
    + video_quality_view_score * vqv_weight_eligibility()
    + photo_expand_score * PHOTO_EXPAND_WEIGHT
    + share_score * SHARE_WEIGHT
    + share_via_dm_score * SHARE_VIA_DM_WEIGHT
    + share_via_copy_link_score * SHARE_VIA_COPY_LINK_WEIGHT
    + dwell_time * CONT_DWELL_TIME_WEIGHT
    + follow_author_score * FOLLOW_AUTHOR_WEIGHT
```

Diversifying content types = hitting multiple score components = higher total scores.

**Checkpoint**: Document your 4 pillars with 10 specific post ideas each.

---

## Step 2.2: Posting Schedule Optimization

### Action
Space posts to avoid the Author Diversity Penalty.

### Algorithm Component
```rust
// From author_diversity_scorer.rs
fn multiplier(&self, position: usize) -> f64 {
    (1.0 - self.floor) * self.decay_factor.powf(position as f64) + self.floor
}

// Effect on multiple posts from same author in a scoring batch:
// Post 1: multiplier = 1.0 (full score)
// Post 2: multiplier = ~0.7 (reduced)
// Post 3: multiplier = ~0.5 (further reduced)
// Post 4: multiplier = ~0.35 (significantly reduced)
```

### Optimal Schedule
```
Minimum gap between posts: 3-4 hours
Maximum posts per day: 3-4
Best practice: 2-3 high-quality posts spaced throughout day

Sample Schedule:
- 8:00 AM: Educational/Thread content
- 1:00 PM: Hot take/Opinion content
- 6:00 PM: Visual/Video content
```

### Why This Works
Posts enter different scoring batches when spaced out, avoiding the exponential decay multiplier that punishes rapid posting.

**Checkpoint**: Set up scheduling tool with optimal time gaps.

---

## Step 2.3: Video Content Strategy

### Action
Create video content that qualifies for VQV weight bonus.

### Algorithm Component
```rust
// From weighted_scorer.rs
fn vqv_weight_eligibility(candidate: &PostCandidate) -> f64 {
    if candidate
        .video_duration_ms
        .is_some_and(|ms| ms > p::MIN_VIDEO_DURATION_MS)
    {
        p::VQV_WEIGHT  // Additional weight applied
    } else {
        0.0  // No bonus for short videos
    }
}
```

### Video Requirements
- **Minimum duration**: Exceed the platform threshold (likely 30-45+ seconds based on industry standards)
- **Optimal duration**: 45 seconds to 2 minutes (long enough for VQV, short enough for completion)
- **Hook in first 3 seconds**: Determines if users watch long enough to trigger quality view

### Video Content Types That Work
1. **Tutorial clips** - "How to [X] in 60 seconds"
2. **Before/after reveals** - Visual transformation
3. **Screen recordings** - Showing a process
4. **Talking head insights** - Direct-to-camera value
5. **Slideshow narratives** - Text on screen with music

**Checkpoint**: Create your first 3 videos following these specs.

---

# Phase 3: Launch & Initial Growth (Days 8-21)

## Step 3.1: The First Post Strategy

### Action
Your first posts must generate engagement signals to train the model.

### Algorithm Component
```python
# From recsys_model.py - The model learns from your engagement history
history_seq_len: int = 128  # Last 128 engagements inform recommendations

# Your first posts create the initial training signal for:
# - Your author embedding (what kind of creator you are)
# - Which user embeddings match with your content
```

### First Week Post Strategy
| Day | Post Type | Goal |
|-----|-----------|------|
| 1 | Strong opinion in niche | Generate replies |
| 2 | Valuable list/tips | Generate saves/shares |
| 3 | Personal story + lesson | Generate likes + follows |
| 4 | Video tutorial | Trigger VQV weight |
| 5 | Controversial (safe) take | Generate quotes + replies |
| 6 | Thread (5-10 posts) | Maximize dwell time |
| 7 | Summary/reflection | Profile clicks + follows |

### Launch Amplification
For first 5 posts, immediately after publishing:
1. Reply to your own post with additional context (creates reply signal)
2. Share in relevant communities/group chats (seeds initial engagement)
3. Engage with 10 accounts in your niche (builds reciprocal awareness)

**Checkpoint**: Publish 7 posts following this exact sequence.

---

## Step 3.2: Strategic Engagement for Discovery

### Action
Engage with accounts to get discovered by the Phoenix retrieval system.

### Algorithm Component
```python
# Phoenix retrieval uses semantic similarity
# When you engage with users in your niche:
# 1. You appear in their notifications (direct visibility)
# 2. Your content becomes semantically linked to their audience
# 3. Users who engage with them have history that may match your content

# User action sequence includes:
history_actions: jax.typing.ArrayLike  # What actions users took
history_author_embeddings: jax.typing.ArrayLike  # Which authors they engaged with
```

### Daily Engagement Routine
```
Morning (30 min):
- Reply thoughtfully to 10 larger accounts in niche
- Quote tweet 2 posts with added value
- Like 20 posts from target audience members

Afternoon (15 min):
- Reply to all comments on your posts (triggers reply signal on their end)
- Engage with anyone who engaged with you

Evening (15 min):
- Find and engage with emerging posts in niche
- Reply to trending topics in your space
```

### Reply Quality Framework
Bad: "Great post!" (no value, won't get engagement)
Good: "This is exactly right. I'd add that [specific insight]. We saw this when [personal example]."

Quality replies:
1. Get liked (signals your value to the author's audience)
2. Get replied to (you appear in more feeds)
3. Generate profile clicks (pathway to follows)

**Checkpoint**: Complete daily engagement routine for 14 consecutive days.

---

## Step 3.3: Thread Strategy for Maximum Dwell Time

### Action
Create threads that maximize the continuous `dwell_time` signal.

### Algorithm Component
```rust
// Dwell time is CONTINUOUS, not binary
+ Self::apply(s.dwell_time, p::CONT_DWELL_TIME_WEIGHT)

// Unlike likes (0 or 1), dwell time compounds:
// 5 seconds of reading = small signal
// 30 seconds of reading = medium signal
// 2 minutes of reading = strong signal
```

### Thread Architecture
```
Post 1 (Hook): Provocative claim + promise
"I spent 100 hours analyzing [X]. Here's what nobody talks about:"

Posts 2-8 (Value): One insight per post
- Each post is self-contained but builds on previous
- Use line breaks for readability
- Include specifics (numbers, examples)

Post 9 (Summary): Recap key points
"TL;DR:
1. [Key point 1]
2. [Key point 2]
3. [Key point 3]"

Post 10 (CTA): Drive action
"If you found this valuable:
1. Follow for more [niche] insights
2. Repost the first tweet to help others find this"
```

### Thread Length Sweet Spot
- **Minimum**: 5 posts (enough to generate significant dwell)
- **Optimal**: 7-10 posts (high dwell without drop-off)
- **Maximum**: 15 posts (beyond this, completion rates drop)

**Checkpoint**: Publish 2 threads per week following this structure.

---

# Phase 4: Growth Acceleration (Days 22-45)

## Step 4.1: Leverage the In-Network Advantage

### Action
Convert out-of-network discovery into in-network advantage.

### Algorithm Component
```rust
// From oon_scorer.rs
let updated_score = c.score.map(|base_score| match c.in_network {
    Some(false) => base_score * p::OON_WEIGHT_FACTOR,  // Penalty < 1.0
    _ => base_score,  // Full score for followers
});
```

### In-Network Math
```
If OON_WEIGHT_FACTOR = 0.5 (example):
- Post shown to non-follower: score × 0.5
- Post shown to follower: score × 1.0

A follower is worth 2x the distribution potential per impression.
```

### Follower Conversion Tactics
1. **End threads with follow CTA**: "Follow for more [topic]"
2. **Create series content**: "Part 1 of my [X] series - follow to catch Part 2"
3. **Tease future content**: "Tomorrow I'm sharing [valuable thing]. Follow so you don't miss it"
4. **Direct ask in viral moments**: When a post performs well, quote it with "If this resonated, I share [topic] daily. Follow along."

### Target Metrics
- Follower conversion rate: 1-3% of profile visitors
- Daily follower goal: Start at 20/day, scale to 100+/day

**Checkpoint**: Track follower conversion rate and optimize profile elements.

---

## Step 4.2: Content Recycling System

### Action
Systematically recycle and repurpose top-performing content.

### Algorithm Component
```rust
// From age_filter.rs - Posts expire after threshold
pub struct AgeFilter {
    pub max_age: Duration,  // Likely ~24 hours
}

// From previously_seen_posts_filter.rs
// Uses bloom filter - probabilistic, not 100% accurate
// Different user cohorts = different bloom filters
```

### Recycling Strategy
```
Week 1: Original post performs well
Week 3-4: Repost with slight modification
Week 8: Transform into different format (thread → single post, text → video)
Week 12: Post again to new follower cohort

Why this works:
1. Age filter resets - post is "new" again
2. Bloom filter is per-user - new followers never saw original
3. Different framing = different engagement patterns
```

### Repurposing Matrix
| Original Format | Repurpose To | When |
|-----------------|--------------|------|
| Viral tweet | Thread expanding on it | 3 days later |
| Thread | Video summarizing it | 1 week later |
| Video | Screenshot + key quote | 2 weeks later |
| Any top performer | Slight reword + repost | 3-4 weeks later |

**Checkpoint**: Create a content database tracking all posts and performance for recycling.

---

## Step 4.3: Negative Signal Avoidance

### Action
Actively minimize negative engagement signals.

### Algorithm Component
```rust
// From weighted_scorer.rs - Negative weights SUBTRACT from score
- Self::apply(s.not_interested_score, p::NOT_INTERESTED_WEIGHT)
- Self::apply(s.block_author_score, p::BLOCK_AUTHOR_WEIGHT)
- Self::apply(s.mute_author_score, p::MUTE_AUTHOR_WEIGHT)
- Self::apply(s.report_score, p::REPORT_WEIGHT)
```

### Behaviors That Trigger Negative Signals
| Behavior | Likely Result | How to Avoid |
|----------|---------------|--------------|
| Posting too frequently | Mute | Max 3-4 posts/day |
| Overly political content | Block/Mute | Stay in your lane |
| Aggressive/hostile replies | Block/Report | Be constructive |
| Spammy self-promotion | Not Interested/Mute | 80% value, 20% promotion |
| Misleading claims | Report | Be accurate |
| Engagement bait | Not Interested | Deliver on promises |

### Content Review Checklist
Before posting, ask:
- [ ] Would this make anyone unfollow/mute me?
- [ ] Am I delivering value or just seeking engagement?
- [ ] Is this on-brand for my niche?
- [ ] Would I be proud of this post in 6 months?

**Checkpoint**: Review last 20 posts for potential negative signal triggers.

---

## Step 4.4: Collaboration for Network Effects

### Action
Collaborate with other creators to access their follower networks.

### Algorithm Component
```python
# When another creator engages with you publicly:
# 1. Their followers see you in their feed (direct exposure)
# 2. Your content enters training data for their audience's user embeddings
# 3. Phoenix retrieval may match you to similar audiences

# From recsys_model.py
history_author_embeddings: jax.typing.ArrayLike
# Users who engage with Creator A may now match with you
```

### Collaboration Types
1. **Quote tweet exchanges**: Agree to quote each other's best content
2. **Thread contributions**: Guest posts in each other's threads
3. **Spaces/Audio rooms**: Co-host discussions in your niche
4. **Challenge/Series collaborations**: Create content series together
5. **Shoutout exchanges**: Direct recommendations to each other's audiences

### Collaboration Targets
- **Sweet spot**: Creators with 2-10x your follower count
- **Not too big**: 100x+ rarely collaborate with small accounts
- **Not too small**: Similar-sized accounts have limited additional reach
- **Same niche**: Audience overlap = higher follow conversion

**Checkpoint**: Reach out to 10 potential collaborators, secure 2-3 partnerships.

---

# Phase 5: Scale to 10K (Days 46-90)

## Step 5.1: Viral Content Engineering

### Action
Systematically engineer posts for viral potential.

### Algorithm Component
```rust
// Posts go viral when they score high across MULTIPLE signals:
final_score = Σ(weight × P(action))

// Viral posts typically excel in:
// - High P(retweet) → spreads to new networks
// - High P(reply) → discussion drives visibility
// - High P(quote) → commentary spreads further
// - High dwell_time → signals quality to algorithm
// - High P(share_via_*) → private shares = quality signal
```

### Viral Post Framework
```
STRUCTURE:
1. Hook (stops scroll) → drives dwell_time
2. Tension/Curiosity (keeps reading) → more dwell_time
3. Insight (delivers value) → triggers like
4. Shareability (others need to see) → triggers retweet/share
5. Discussion catalyst (invites response) → triggers reply

VIRAL TRIGGERS:
□ Contrarian take on accepted wisdom
□ Specific numbers/data that surprise
□ "Hidden" information being revealed
□ Personal story with universal lesson
□ Simple framework for complex problem
□ Prediction about the future
□ Calling out common mistake
```

### Viral Post Templates
**Template 1: The Myth Buster**
```
[Common belief] is completely wrong.

Here's what actually happens:
[Insight 1]
[Insight 2]
[Insight 3]

I learned this after [personal experience].
```

**Template 2: The Numbered Insight**
```
I [impressive action] in [time period].

[Number] things I wish I knew earlier:

1. [Insight] - [why it matters]
2. [Insight] - [why it matters]
...

Which resonates most with you?
```

**Template 3: The Contrarian**
```
Unpopular opinion: [contrarian take]

Here's why everyone gets this wrong:
[Explanation with evidence]

Reply with your take 👇
```

**Checkpoint**: Create 10 posts using viral templates, track which perform best.

---

## Step 5.2: Momentum Maintenance

### Action
Maintain posting consistency to preserve algorithmic momentum.

### Algorithm Component
```rust
// From thunder_source.rs - In-network source
// Maintains recent posts from followed accounts
// Auto-trims posts older than retention period

// Consistent posting keeps you in the candidate pool
// Gaps in posting = gaps in visibility
```

### Consistency Requirements
| Metric | Minimum | Optimal |
|--------|---------|---------|
| Posts per day | 1 | 2-3 |
| Threads per week | 1 | 2-3 |
| Videos per week | 1 | 2-3 |
| Days without posting | Max 1 | 0 |
| Engagement time daily | 30 min | 60 min |

### Content Buffer System
```
Maintain at all times:
- 7 days of scheduled posts
- 3 ready-to-post threads
- 5 evergreen posts for slow days
- 2 videos in production

This prevents gaps that break momentum.
```

**Checkpoint**: Build 2-week content buffer.

---

## Step 5.3: Analytics-Driven Optimization

### Action
Use performance data to continuously improve content.

### Algorithm Component
```
The algorithm learns from engagement signals.
Your job: analyze which content generates highest signals, then do more of that.

Key metric correlations:
- Impressions ∝ Algorithm distribution score
- Engagement rate = (likes + replies + retweets) / impressions
- Profile visits ∝ profile_click_score triggering
- Follows ∝ follow_author_score
```

### Weekly Analytics Review
```
1. Top 5 posts by impressions → What made algorithm distribute them?
2. Top 5 posts by engagement rate → What made people interact?
3. Bottom 5 posts → What went wrong?
4. Profile visits trend → Is content driving curiosity?
5. Follower growth rate → Is growth accelerating or decelerating?

Action items from each review:
- Double down on top content patterns
- Eliminate bottom content patterns
- Optimize based on profile visit → follow conversion
```

### A/B Testing Framework
```
Test one variable at a time:
- Posting time (morning vs evening)
- Hook style (question vs statement vs number)
- Format (text vs image vs video)
- Length (short vs long)
- CTA inclusion (with vs without)

Run each test for 2 weeks with 10+ posts per variation.
```

**Checkpoint**: Establish weekly analytics review habit.

---

## Step 5.4: Monetization Foundation

### Action
Build monetization pathways before reaching 10K.

### Why Before 10K?
```
At 10K followers:
- Platform monetization unlocks (ads revenue sharing)
- Sponsor interest triggers
- Product launch becomes viable

Building infrastructure before 10K means you can monetize immediately upon arrival.
```

### Monetization Pathways

**Path 1: Platform Revenue**
- Requirements: 500+ followers, 5M impressions in 3 months
- Action: Focus on impressions (algorithmic distribution)
- Prepare: Verify account, set up payment

**Path 2: Sponsorships/Brand Deals**
- Requirements: Engaged niche audience
- Action: Build media kit with engagement metrics
- Prepare: Create rate card, identify target brands

**Path 3: Digital Products**
- Requirements: Demonstrated expertise
- Action: Document your process/knowledge
- Prepare: Outline course/ebook/template based on top content

**Path 4: Services**
- Requirements: Proven results in niche
- Action: Collect testimonials, document case studies
- Prepare: Service offering, pricing, booking system

**Path 5: Community/Subscription**
- Requirements: Loyal engaged audience
- Action: Identify what people would pay for
- Prepare: Exclusive content plan, community platform choice

### Pre-10K Monetization Checklist
- [ ] Media kit created with stats
- [ ] 1 digital product outlined
- [ ] Service offering defined
- [ ] Email list started (capture leads off-platform)
- [ ] Payment processing set up
- [ ] 3 potential sponsor targets identified

**Checkpoint**: Complete pre-10K monetization checklist.

---

# Phase 6: Final Push to 10K (Days 91-120)

## Step 6.1: Growth Sprint Strategy

### Action
Execute focused growth sprints to accelerate final push.

### Algorithm Component
```
Compound growth mechanics:
- More followers → more in-network distribution
- More distribution → more impressions
- More impressions → more engagement
- More engagement → higher algorithm scores
- Higher scores → even more distribution

The flywheel accelerates as you approach 10K.
```

### 30-Day Sprint Plan
```
Week 1: Content Blitz
- 4 posts per day (max sustainable)
- 2 threads
- 3 videos
- 5 collaborations
Goal: Maximize content surface area

Week 2: Engagement Blitz
- 2 hours daily engagement
- Reply to every comment within 1 hour
- Initiate 20 conversations daily
Goal: Maximize relationship building

Week 3: Viral Attempts
- Post 10 viral-optimized posts
- Leverage trending topics
- Quote tweet major accounts
Goal: Catch one viral wave

Week 4: Conversion Focus
- Optimize all CTAs
- Run follow-back engagement
- Create irresistible pinned post
Goal: Maximize follower conversion
```

**Checkpoint**: Execute 30-day sprint, track daily metrics.

---

## Step 6.2: Audience Retention for Sustainable Monetization

### Action
Ensure followers stay engaged for long-term monetization.

### Algorithm Component
```rust
// Your posts compete for attention in follower feeds
// In-network gives advantage, but still must score well
// Disengaged followers = lower engagement rates = lower scores

// From author_diversity_scorer.rs
// Even followers see diminished scores for low-quality posts
```

### Retention Tactics
1. **Consistency in value**: Every post must deliver on your niche promise
2. **Community building**: Reply to followers, remember regulars
3. **Exclusive value**: Give followers content non-followers don't get
4. **Personality**: Be human, share wins and losses
5. **Ask for input**: Polls, questions, letting audience shape content

### Engagement Rate Benchmarks
| Follower Count | Good Engagement Rate | Excellent Rate |
|----------------|---------------------|----------------|
| 0-1K | 5-10% | 10%+ |
| 1K-5K | 3-5% | 5%+ |
| 5K-10K | 2-3% | 3%+ |

If engagement rate drops, focus on quality over quantity.

**Checkpoint**: Track engagement rate weekly, maintain above benchmarks.

---

## Step 6.3: The 10K Milestone

### Action
Celebrate and capitalize on reaching 10K.

### 10K Announcement Post
```
[Number] of you are here now.

[Brief reflection on journey]
[Thank followers authentically]
[Reiterate value you provide]
[Hint at what's coming next]

Let's keep going.
```

### Immediate 10K Actions
1. **Update bio**: Add "10K" if relevant to credibility
2. **Announce milestone**: Creates engagement + attracts new followers
3. **Activate monetization**: Launch prepared products/services
4. **Pitch sponsors**: "10K engaged followers in [niche]"
5. **Set next goal**: 25K, 50K, 100K

**Checkpoint**: Complete 10K milestone actions within 48 hours of hitting target.

---

# Quick Reference: Algorithm Cheat Sheet

## Positive Signals (Maximize These)
| Signal | Weight Category | How to Trigger |
|--------|-----------------|----------------|
| `P(favorite)` | Standard | Create likeable content |
| `P(reply)` | Standard | Ask questions, make claims |
| `P(repost)` | High | Create shareable insights |
| `P(quote)` | Standard | Make discussion-worthy posts |
| `P(video_quality_view)` | Bonus | Videos > min duration |
| `P(share_via_dm)` | Standard | Create "send to a friend" content |
| `P(dwell_time)` | Continuous | Threads, long-form, detailed images |
| `P(profile_click)` | Standard | Be intriguing, incomplete CTA |
| `P(follow)` | Standard | Demonstrate ongoing value |

## Negative Signals (Avoid These)
| Signal | Impact | Prevention |
|--------|--------|------------|
| `P(not_interested)` | Negative | Stay on-niche, deliver value |
| `P(block)` | Strong negative | Don't be hostile/spammy |
| `P(mute)` | Negative | Don't overpost, stay valuable |
| `P(report)` | Strong negative | Follow platform rules |

## Key Mechanics
| Mechanic | Impact | Optimization |
|----------|--------|--------------|
| Author Diversity | Exponential decay for multiple posts | Space posts 3-4 hours apart |
| In-Network Bonus | Full score vs reduced OON score | Convert followers aggressively |
| Age Filter | Posts expire after ~24 hours | Post consistently |
| VQV Weight | Bonus for qualifying videos | Videos > 45 seconds |

---

# Success Metrics by Phase

| Phase | Days | Follower Target | Key Metric |
|-------|------|-----------------|------------|
| Foundation | 1-3 | 0 | Profile complete |
| Content Setup | 4-7 | 0 | Content system ready |
| Launch | 8-21 | 100-500 | First viral post |
| Acceleration | 22-45 | 500-2,000 | Consistent growth |
| Scale | 46-90 | 2,000-7,000 | 50+ followers/day |
| Final Push | 91-120 | 7,000-10,000 | 100+ followers/day |

---

# Daily Checklist

```
□ Post 2-3 pieces of content (spaced 3-4 hours)
□ Reply to all comments on your posts
□ Engage with 10 larger accounts in niche
□ Engage with 10 peers/similar-sized accounts
□ Check analytics for top/bottom performers
□ Add 1 post to content buffer
□ Review and respond to DMs
□ Track follower count
```

---

*This playbook is based on analysis of X's open-source recommendation algorithm. Algorithm weights and thresholds may change; principles remain consistent.*
