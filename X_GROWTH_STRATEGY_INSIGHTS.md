# X Algorithm Insights: Growing a New Account

## Executive Summary

After analyzing X's open-source recommendation algorithm, here are the key insights for growing a brand new X.com account. The algorithm is ML-first with a Grok-based transformer at its core - understanding how it evaluates content is crucial for growth.

---

## Part 1: How the Algorithm Works (The Basics)

### Two Sources of Distribution

1. **In-Network (Thunder)**: Posts shown to your followers
2. **Out-of-Network (Phoenix)**: Posts discovered and shown to non-followers

**Critical Insight**: New accounts primarily need to crack the **Out-of-Network (Phoenix)** system since they have few followers. This is where viral discovery happens.

### The Scoring Formula

Every post gets a score based on predicted engagement:

```
Final Score = Σ (weight × P(action))

Where actions include:
+ P(favorite/like)       [POSITIVE]
+ P(reply)               [POSITIVE]
+ P(repost/retweet)      [POSITIVE]
+ P(quote)               [POSITIVE]
+ P(click)               [POSITIVE]
+ P(profile_click)       [POSITIVE]
+ P(video_quality_view)  [POSITIVE - only for videos above min duration]
+ P(photo_expand)        [POSITIVE]
+ P(share)               [POSITIVE]
+ P(share_via_dm)        [POSITIVE]
+ P(share_via_copy_link) [POSITIVE]
+ P(dwell_time)          [POSITIVE - continuous]
+ P(follow_author)       [POSITIVE]
- P(not_interested)      [NEGATIVE]
- P(block_author)        [NEGATIVE]
- P(mute_author)         [NEGATIVE]
- P(report)              [NEGATIVE]
```

---

## Part 2: Key Virality Insights

### Insight #1: The ML Model Learns From Engagement History

The transformer model considers your **last 128 engagements** when deciding what to show users:
- What posts they liked
- What authors they engaged with
- What types of engagement (like, reply, repost, click)
- Where they engaged (home feed, search, notifications)

**Actionable**: Create content that matches patterns of what your target audience already engages with. The algorithm learns implicit preferences from behavior, not stated interests.

### Insight #2: In-Network Content Has Priority

```rust
// From oon_scorer.rs
let updated_score = c.score.map(|base_score| match c.in_network {
    Some(false) => base_score * p::OON_WEIGHT_FACTOR,  // Multiplied by < 1.0
    _ => base_score,  // Full score for in-network
});
```

**Key Finding**: Out-of-network posts (from non-followed accounts) are multiplied by a factor < 1.0. This means even excellent out-of-network content starts at a disadvantage.

**Actionable**:
- Building followers is crucial - each follower gives your content full scoring potential
- Early followers are disproportionately valuable for breaking into feeds

### Insight #3: Author Diversity Penalty

```rust
// From author_diversity_scorer.rs
fn multiplier(&self, position: usize) -> f64 {
    (1.0 - self.floor) * self.decay_factor.powf(position as f64) + self.floor
}
```

When multiple posts from the same author are in a batch:
- 1st post: Full score (multiplier = 1.0)
- 2nd post: Reduced score (exponential decay)
- 3rd+ posts: Further reduced

**Actionable**:
- Quality over quantity - one excellent post beats several mediocre ones
- Space out your posts rather than posting in rapid succession
- Each post is an independent opportunity; don't cannibalize yourself

### Insight #4: Content Freshness Matters

```rust
// From age_filter.rs
pub struct AgeFilter {
    pub max_age: Duration,
}
```

Posts older than a threshold (likely ~24 hours based on typical feed behavior) are filtered out entirely.

**Actionable**:
- Post consistently to maintain presence in the candidate pool
- Time-sensitive or trending content has a short window
- Evergreen content won't resurface automatically - you may need to repost/reference it

### Insight #5: Video Gets Special Treatment

```rust
// From weighted_scorer.rs
fn vqv_weight_eligibility(candidate: &PostCandidate) -> f64 {
    if candidate
        .video_duration_ms
        .is_some_and(|ms| ms > p::MIN_VIDEO_DURATION_MS)
    {
        p::VQV_WEIGHT
    } else {
        0.0
    }
}
```

Videos above a minimum duration threshold get an additional score boost (VQV = Video Quality View weight).

**Actionable**:
- Create videos longer than the minimum duration threshold
- Video content has an algorithmic advantage over text-only posts
- Short-form video is NOT penalized, but quality views on longer video is rewarded

### Insight #6: Shares Are Heavily Weighted

The algorithm tracks multiple share types separately:
- `share_score`
- `share_via_dm_score`
- `share_via_copy_link_score`

**Actionable**:
- Create shareable content (content people want to send to friends)
- DM shares and link copies are tracked as separate positive signals
- "Share with a friend who..." style content can drive these metrics

### Insight #7: Dwell Time Is a Continuous Signal

```rust
+ Self::apply(s.dwell_time, p::CONT_DWELL_TIME_WEIGHT)
```

Unlike binary actions (like/no-like), dwell time is continuous - the longer someone spends on your post, the higher the signal.

**Actionable**:
- Create content that takes time to consume (threads, detailed images, longer videos)
- Make content that rewards careful reading/watching
- Avoid low-effort posts that get scrolled past quickly

### Insight #8: Profile Clicks Signal Discovery Value

```rust
+ Self::apply(s.profile_click_score, p::PROFILE_CLICK_WEIGHT)
```

When users click through to your profile after seeing your post, it's a positive signal.

**Actionable**:
- Create curiosity about who you are
- Don't give everything away in one post - make people want to learn more
- An intriguing bio and profile setup converts profile clicks to follows

### Insight #9: Follow-From-Post Is Tracked

```rust
+ Self::apply(s.follow_author_score, p::FOLLOW_AUTHOR_WEIGHT)
```

The algorithm specifically tracks when a post leads to a follow.

**Actionable**:
- Create "follow-worthy" content that demonstrates ongoing value
- First impressions matter - your breakthrough post should represent your best work
- Consider including soft CTAs for following when appropriate

---

## Part 3: What Gets Filtered (Things to Avoid)

### Hard Filters (Content Never Shown)

| Filter | What It Removes |
|--------|-----------------|
| `AgeFilter` | Posts older than threshold |
| `MutedKeywordFilter` | Posts containing user's muted keywords |
| `AuthorSocialgraphFilter` | Posts from blocked/muted accounts |
| `VFFilter` | Deleted, spam, violence, gore content |
| `SelfpostFilter` | User's own posts (won't see in own feed) |
| `PreviouslySeenPostsFilter` | Posts user already viewed |

### Soft Penalties (Score Reduction)

| Behavior | Effect |
|----------|--------|
| `P(not_interested)` | Negative weight applied |
| `P(block_author)` | Strong negative weight |
| `P(mute_author)` | Negative weight |
| `P(report)` | Negative weight |

**Actionable**:
- Avoid controversial content that triggers mutes/blocks
- Don't use commonly muted keywords
- Stay within safety guidelines to avoid VF filtering
- Polarizing content might get engagement but also gets blocks - net effect can be negative

---

## Part 4: New Account Challenges

### Challenge #1: No Historical Signal

The ML model learns from historical user-post interactions. A new account with no engagement history has less training signal for the model to learn from.

**Solution**:
- Focus on niches where you can quickly build an engagement corpus
- Engage with others in your target community to build reciprocal awareness
- Your first 100 engagements on your posts are disproportionately valuable for model training

### Challenge #2: No Follower Base

Without followers, you can't leverage the in-network advantage.

**Solution**:
- Focus entirely on out-of-network discovery initially
- Create content that matches existing engagement patterns of target users
- Each new follower expands your in-network reach exponentially

### Challenge #3: Cold Start on Retrieval

The Phoenix retrieval system uses a two-tower model where:
- User tower = user + history → embedding
- Candidate tower = post + author → embedding
- Similarity search finds matches

New accounts with unknown authors have less developed author embeddings.

**Solution**:
- The post embedding matters too - create content semantically similar to what your target audience engages with
- Author embedding develops over time as people engage
- Consistency in topic/niche helps build a coherent author embedding

---

## Part 5: Growth Strategies Based on Algorithm Design

### Strategy 1: The "Engagement Cascade"

The algorithm predicts multiple engagement types. Create content that triggers **chains**:

```
Great hook → stops scroll (dwell)
    → interesting content (click/expand)
    → valuable insight (like)
    → discussion-worthy (reply)
    → shareable (repost/share)
    → follow-worthy (profile click → follow)
```

Each step compounds the score.

### Strategy 2: Optimize for Video

Given the special VQV treatment:
1. Create video content above the minimum duration threshold
2. Make the first few seconds compelling (affects whether people watch long enough)
3. Video gives you an algorithmic boost that text-only can't access

### Strategy 3: Build In-Network Distribution

Since in-network content has full scoring potential:
1. Focus initially on converting views to follows
2. Each follower is a multiplier on future content reach
3. Engage authentically with potential followers in your niche

### Strategy 4: Leverage Reply Engagement

The model tracks `P(reply)` as a positive signal:
1. Create content that invites responses
2. Ask questions
3. Make provocative (but not controversial) statements
4. Reply to your own posts with additional context (creates conversation threads)

### Strategy 5: Maximize Dwell Time

Since dwell is a continuous signal:
1. Use threads - they take time to read
2. Include detailed images that reward zooming/studying
3. Write longer-form content that can't be skimmed
4. Use formatting (lists, spacing) that keeps people reading

### Strategy 6: Create Share-Worthy Content

Multiple share types are tracked:
1. "Tag someone who..." posts drive shares
2. Valuable/useful content gets DM'd to friends
3. Controversial-but-safe takes get quoted/shared
4. Tutorials and how-tos get link-copied

### Strategy 7: Avoid the Diversity Penalty

Your posts compete with each other:
1. Don't post 5 things in 30 minutes
2. Space posts out over hours/days
3. Make each post your best effort
4. Delete underperforming posts rather than letting them dilute your average

### Strategy 8: Leverage the Profile Click Signal

Make profile clicks convert to follows:
1. Compelling bio that explains your value
2. Pinned post that showcases your best work
3. Consistent posting history that shows you're worth following
4. Clear niche/topic so people know what to expect

---

## Part 6: What the Algorithm Does NOT Consider

Based on the codebase analysis, these are **NOT** explicit ranking factors:

| Factor | Notes |
|--------|-------|
| Account age | No explicit penalty/boost for new accounts |
| Verified/blue status | Not visible in ranking code |
| Follower count | Fetched but not explicitly weighted in scores |
| Hashtags | No special treatment in scoring |
| URLs/links | No special treatment |
| Tweet word count | Not a direct factor |
| Time of day posted | Not in scoring (but affects who's online) |
| Geographic signals | Not in scoring (but locale is available) |

**Note**: These may influence the ML model implicitly through training, but they're not hand-engineered features.

---

## Part 7: Quick Reference - Do's and Don'ts

### DO:
- Create video content (above min duration)
- Space out your posts
- Engage in ways that drive replies
- Create shareable/saveable content
- Build a coherent niche (helps author embedding)
- Optimize your profile for follow conversion
- Focus on content that matches your target audience's existing engagement patterns

### DON'T:
- Post rapidly in succession (diversity penalty)
- Create controversial content that triggers blocks/mutes
- Use commonly muted keywords
- Ignore video as a format
- Post low-effort content that gets scrolled past
- Neglect your profile setup

---

## Conclusion

The X algorithm is fundamentally about **predicting engagement**. It asks: "If I show this post to this user, what will they do?"

For new accounts, success comes from:
1. Creating content that matches existing engagement patterns of target audiences
2. Maximizing positive engagement signals (especially shares, replies, and dwell time)
3. Avoiding negative signals (blocks, mutes, reports)
4. Converting every impression into a potential follower
5. Leveraging video for the algorithmic boost

The algorithm has no explicit new-account penalty, but new accounts lack the historical signal that established accounts have. Focus on building that signal quickly through consistent, high-quality, niche-focused content that drives authentic engagement.

---

*Analysis based on X's open-source recommendation algorithm repository.*
