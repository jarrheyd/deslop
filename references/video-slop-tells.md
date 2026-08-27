# Video Slop Tells

How to detect AI-generated video content across Sora, Veo, Kling, Runway, and other generators. Updated for the current state of AI video (2026).

## The Current State

AI video has matured from short, low-resolution clips with obvious artifacts into production-ready toolsets. Veo 3 generates video with synchronized audio (footsteps, ambient sound, dialogue) from text. Kling 3.0 holds the #1 benchmark score. Detection is harder than it was in 2024, but tells remain.

## Physics Violations

The most reliable detection category. AI understands visual patterns but not physical laws.

### Gravity and Momentum
- Objects fall at inconsistent speeds — sometimes too slow, sometimes with sudden acceleration
- Thrown objects don't follow parabolic arcs
- Liquids pour in straight lines instead of splashing realistically
- Fabric doesn't drape or blow naturally — it moves as a texture, not a material
- **What to look for**: Anything that moves, falls, or flows. Slow the video to 0.25x and watch physics.

### Force and Contact
- Objects pass through each other subtly, especially at edges
- Collision responses are wrong — a ball hitting a wall might bounce at the wrong angle or not deform
- Weight isn't communicated — a heavy box is lifted as easily as an empty one
- **What to look for**: Any moment where two objects interact physically

### Light and Shadow
- Shadows move independently of their source objects
- Light sources change between shots without cuts
- Reflections don't match the environment (mirrors, water, glass)
- Subsurface scattering on skin changes frame to frame
- **What to look for**: Follow one shadow across 3+ seconds. Does it behave consistently?

## Object and Body Artifacts

### Hand and Gesture Issues
Still the weakest point, even in 2026 models. Fingers blend together during motion. Gestures that should be precise (pointing, typing, grasping) lose coherence.
- **What to look for**: Any hand interacting with an object. Fingers during rapid motion. Count fingers frame-by-frame.

### Object Morphing
AI blends held objects into the person's body, especially when objects overlap with hands. A phone slowly merges into a palm. A pen dissolves into fingers.
- **What to look for**: Objects held near the body during movement. Track the object's outline across 2-3 seconds.

### Structural Distortion
Fences, grids, lattices, railings, and any repeating geometric structure exhibit unnatural twisting, interlacing, or morphing. AI doesn't understand structural rigidity.
- **What to look for**: Background architecture. Straight lines that wobble. Repeating patterns that lose consistency.

### Clothing and Fabric
Clothing textures shimmer or crawl over time. Patterns (stripes, plaids, logos) drift across the surface rather than staying anchored to the fabric.
- **What to look for**: Any patterned clothing. Logos that shift position. Stripes that aren't parallel frame to frame.

## Temporal Inconsistencies

### Surface Texture Flickering
High-frequency flickering or drifting over surfaces, manifesting as crawling patterns, grid-like noise, or temporally unstable blur. Most visible on skin, walls, and uniform surfaces.
- **What to look for**: Pause on a wall or floor. Advance frame by frame. Does the texture change when nothing is moving?

### Character Inconsistency
Facial features subtly shift between frames. Eye color, skin tone, jawline, and hair can drift, especially during head turns or across cuts.
- **What to look for**: Scrub back and forth across a head turn. Does the person look slightly different after turning?

### Background Morphing
Environments slowly change when the camera isn't directly focused on them. Buildings shift position. Trees gain or lose branches. Furniture moves.
- **What to look for**: Background elements at the start vs. end of a shot. Take a screenshot of frame 1 and compare to the last frame.

### Inter-Frame Artifacts
Artifacts between frames that are invisible at normal playback speed but detectable in slow motion. Ghosting, doubling, and brief corruption.
- **What to look for**: Slow to 0.25x. Look at edges of moving objects for doubling or transparency artifacts.

## Audio Tells (For Videos with Sound)

### Lip Sync Issues
Even Veo 3's synchronized dialogue has micro-timing issues. Consonants that require lip closure (B, M, P) are the hardest — check if lips actually close.
- **What to look for**: Zoom into the mouth during speech. Do "B" and "M" sounds show full lip closure?

### Environmental Sound Mismatch
Footsteps that don't match the surface. Ambient sound that doesn't change when the camera moves. Echo that's inconsistent with the visible space.
- **What to look for**: Close your eyes and listen. Does the audio describe a different space than the video shows?

### Voice Consistency
AI-generated voices maintain too-perfect consistency in tone and pacing. No mic-handling noise, no room tone changes, no natural volume variation.
- **What to look for**: Is the voice exactly the same volume and quality throughout? Real recording has variation.

## Detection Process

### Quick Check (30 seconds)
1. Watch at normal speed — does anything feel "off"?
2. Look at hands and any held objects
3. Check for any text in the video (signs, screens)
4. Listen to the audio with eyes closed

### Deep Check (2-3 minutes)
1. Slow to 0.25x speed
2. Track one shadow across the full clip
3. Compare first and last frame backgrounds
4. Frame-by-frame any hand-object interaction
5. Check facial consistency across head turns
6. Look for surface texture flickering on walls/floors
7. Verify physics of any moving/falling/flowing elements

### Metadata Check
1. Check file metadata for generation signatures
2. Look for standardized resolution/framerate combos that generators use
3. Check if the exact same "person" appears in other content (character inconsistency)

## When Using AI Video

If you're generating video with AI tools, here's how to minimize tells:
1. **Keep it short.** Longer clips accumulate more temporal artifacts.
2. **Avoid hand close-ups.** Frame around the problem.
3. **Minimize text.** Don't include signs, screens, or readable text.
4. **Use for B-roll, not hero content.** Background footage, transitions, texture — not the main subject.
5. **Heavy post-processing.** Color grade, add film grain, crop, speed ramp. The more you transform the raw output, the less "AI" it reads.
6. **Composite with real footage.** Mix AI-generated elements with real video to mask the tells.
7. **Prefer stylized over realistic.** Animated, illustrated, or heavily stylized video hides AI artifacts better than photorealistic attempts.
