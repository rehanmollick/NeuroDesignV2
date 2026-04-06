"""
Neuroaesthetics knowledge base for Gemini prompt context.

This is NOT a vector database or retrieval system. It's structured text
injected directly into the Gemini prompt so the model has domain expertise
when interpreting brain activation patterns for design evaluation.

Grounded in: Chatterjee & Vartanian (2014) neuroaesthetics framework,
Vessel et al. (2012) aesthetic experience, Reber et al. (2004) processing
fluency theory of aesthetic pleasure.
"""

KNOWLEDGE_BASE = """
## NEUROAESTHETICS KNOWLEDGE BASE FOR DESIGN EVALUATION

### How to interpret brain activation for design quality

You are evaluating two web/UI designs using predicted fMRI brain activation
patterns. The data comes from TRIBE v2 (a model trained to predict brain
responses from visual stimuli). The activation values are jointly normalized
so A and B are directly comparable.

CRITICAL: More total brain activation does NOT mean better design. The
PATTERN of activation matters, not the amount.

### The three neural systems of aesthetic experience

1. SENSORY-MOTOR SYSTEM (visual cortex, parietal attention)
   - Processes visual features: edges, colors, spatial layout, motion
   - High activation = complex visual input
   - Does NOT indicate quality by itself
   - Extreme values suggest visual clutter or overwhelming design

2. EMOTION-VALUATION SYSTEM (orbitofrontal, insula, cingulate)
   - Evaluates reward, pleasure, emotional significance
   - High reward activation = aesthetically pleasing
   - High insula = strong gut reaction (positive or negative)
   - This is the closest signal to "the brain likes this design"

3. MEANING-KNOWLEDGE SYSTEM (angular gyrus, precuneus, temporal pole)
   - Activates for personally meaningful, memorable content
   - Links current perception to existing knowledge and memories
   - High activation = the design connects, it means something
   - Low activation = generic, forgettable

### Composite signal interpretation rules

REWARD (orbitofrontal, orbital sulcus, ventral cingulate):
- High reward = the brain finds this aesthetically pleasing
- Strongest predictor of subjective aesthetic preference
- When reward is high, cognitive load is usually "engagement" not "confusion"

COGNITIVE LOAD (dorsolateral prefrontal, anterior cingulate, middle frontal):
- Ambiguous signal by itself. Depends on context:
  - High load + high reward = engaged, actively processing interesting content
  - High load + low reward = confused, struggling with bad design
  - Low load + high reward = effortless beauty, processing fluency
  - Low load + low reward = boring, disengaged

VISUAL FLUENCY (V1, cuneus, occipital areas):
- Measures visual processing intensity
- Moderate = rich but organized visual content
- Very high = visual overload, too many competing elements
- Very low = minimal visual content (not necessarily good or bad)

SOCIAL TRUST (fusiform, superior temporal sulcus, insula):
- Fusiform = face processing. High means faces are present and noticed.
- Faces in designs build trust and human connection
- Superior temporal sulcus = reading intentions, social perception
- Designs with people/faces almost always score higher on trust

MEMORY (parahippocampal, angular gyrus, precuneus, temporal pole):
- High = memorable, activates meaning-making circuits
- Parahippocampal = scene recognition, spatial context
- Temporal pole = linking emotions to familiar concepts
- Good designs are memorable. High memory is almost always positive.

ATTENTION (superior parietal, intraparietal sulcus, frontal eye fields):
- Measures directed, focused visual attention
- High = strong visual hierarchy, the eye knows where to look
- Low = scattered gaze, no clear focal point
- Good design directs attention intentionally

### Pattern recognition for design quality

GOOD DESIGN patterns:
- High reward + moderate cognitive load + high memory
  = engaging, aesthetically pleasing, memorable
- High attention + moderate visual fluency + high reward
  = clear visual hierarchy with beautiful execution
- High social trust + high reward + high memory
  = faces/people that connect emotionally and stick in memory
- Low cognitive load + high reward + high attention
  = effortlessly beautiful, processing fluency (the gold standard)

BAD DESIGN patterns:
- High visual fluency + high cognitive load + low reward
  = cluttered, confusing, the brain is struggling
- High cognitive load + low reward + low memory
  = hard to process AND not worth the effort
- Low everything
  = boring, generic, nobody will remember this
- High visual fluency + low attention + low memory
  = visually busy but nothing stands out or sticks

AMBIGUOUS patterns (use the images to break the tie):
- Similar scores across all signals
  = both designs produce similar brain responses, look at the images
- High in some areas for A, high in other areas for B
  = different strengths, describe the tradeoffs

### Calibration examples

Example 1: Apple.com vs cluttered e-commerce
- Apple: moderate visual, high reward, low cognitive load, high attention
- Cluttered: high visual, high cognitive load, low reward, scattered attention
- Winner: Apple. Processing fluency + clear hierarchy beats visual noise.

Example 2: Landing page with team photo vs same layout without
- With face: higher social trust (fusiform), higher memory, similar everything else
- Without: neutral across the board
- Winner: With face. Faces build trust and memorability with minimal downside.

Example 3: Dense infographic vs simple text slide
- Infographic: high visual, moderate cognitive load, high memory, high attention
- Text: low visual, low cognitive load, low memory, low attention
- Winner: Infographic. More complex but drives engagement and recall.

### Honest caveats (include in your analysis when relevant)

- TRIBE v2 was trained on video/audio stimuli. Static image input (converted
  to a 1-second still video) is out-of-distribution. Results are directional,
  not absolute. Treat as "brain response tendency" not "exact fMRI measurement."
- Relative comparisons (A vs B) are more reliable than absolute values.
- The model predicts GROUP-AVERAGE responses. Individual brains vary.
- These patterns are based on neuroaesthetics research applied to design.
  They are informed opinions, not medical diagnoses.
"""
