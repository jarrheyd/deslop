# Image Slop Tells

How to detect AI-generated images and how to avoid the tells when using AI image generation tools. Covers photography, illustrations, headshots, product shots, and marketing imagery.

## The Fundamental Problem

AI images have no referent in reality. No moment was captured, no object was arranged, no brushstroke was applied. This ontological shallowness is what makes them feel "off" even when technically flawless. Human observers correctly identify AI images only ~70% of the time consciously, but the uncanny feeling registers subconsciously at much higher rates.

## Human Appearance Tells

### Plastic Skin
The single most recognizable AI image tell. Aggressive denoising strips natural pores, peach fuzz, vellus hair, and micro-imperfections. AI learns a single "skin texture" and applies it universally — real skin varies between forehead, cheek, jawline, and neck.
- **What to look for**: Poreless, waxy complexion. Uniform texture across face. Complete absence of fine body hair. Skin that looks like it was shot through a diffusion filter.
- **In prompts**: Specify "natural skin texture with visible pores," "imperfect skin," "photojournalistic quality." Avoid "beautiful," "flawless," "studio quality" which amplify the smoothing.
- **In post**: Add subtle noise/grain. Reduce clarity slightly. Never use AI "enhance" or "upscale" features on faces.

### Uncanny Symmetry
Real faces are asymmetrical — one eye slightly higher, one nostril slightly wider, one ear slightly different. AI faces are unnervingly balanced.
- **What to look for**: Too-perfect bilateral symmetry. Mirror-image quality between left and right face.
- **In prompts**: "Candid photo," "caught mid-expression," "natural asymmetry." Avoid front-facing poses which maximize the symmetry problem.

### Dead Eyes
Eyes that are technically correct but emotionally hollow. Pupils that don't quite track. Catchlights that are inconsistent with the lighting.
- **What to look for**: Both eyes reflecting different light sources. Pupils at slightly different sizes without medical explanation. Gaze direction that doesn't quite match head orientation.
- **In prompts**: Specify actual emotions and contexts rather than poses. "Laughing at something off-camera" beats "smiling portrait."

### Hair as Mass
AI renders hair as a single smooth volume rather than individual strands with flyaways, frizz, and natural disorder.
- **What to look for**: Hair that moves as one piece. No flyaway strands. Perfect uniformity in curl pattern. Hair that doesn't interact naturally with ears, shoulders, or wind.
- **In prompts**: "Messy hair," "wind-blown," "natural hair with flyaways." Avoid "perfect hair," "sleek."

### Teeth and Mouth
Teeth that are too uniform, too white, or that merge together. Lips with no natural variation in moisture or color.
- **What to look for**: All teeth the same size and shape. Gum line that's too even. Lower teeth (often forgotten by AI) that look wrong.

## Structural/Anatomical Tells

### Hands and Fingers
Significantly improved in 2025-2026 (Midjourney V7, DALL-E 3) but not eliminated. Extra fingers, melting digits, impossible joint angles still appear, especially in complex hand positions.
- **What to look for**: Count fingers. Check joint angles. Look at how hands interact with objects — objects often merge into the hand.
- **In prompts**: Keep hands in simple, natural positions. Holding a coffee cup is easier than playing guitar. Hands in pockets avoid the problem entirely.

### Jewelry and Accessories
Rings, earrings, necklaces, and glasses that merge into skin or defy physics. Chains with impossible links. Earring backs that penetrate through the earlobe.
- **What to look for**: Where accessories meet skin. Whether clasps, posts, and links are physically possible.

### Text in Images
AI text rendering has improved (DALL-E is ~95-100% accurate) but Midjourney and others still produce gibberish or near-miss text. Letters that almost spell something but don't.
- **What to look for**: Text on signs, shirts, books, screens. Zoom in — letters may be subtly wrong.
- **In prompts**: If text must appear, use DALL-E or Flux which handle text better. Or plan to composite real text in post.

## Composition and Style Tells

### Hyper-HDR Look
Over-processed, oversaturated appearance. Every shadow lifted, every highlight tamed. The dynamic range feels artificially compressed.
- **What to look for**: Shadows that are too bright. Colors that pop unnaturally. A "too clean" quality to the lighting.
- **Fix**: Desaturate slightly. Crush the blacks. Let shadows be shadows. Real photography has contrast.

### Generic Compositions
AI defaults to the most common framing from training data: centered subject, rule-of-thirds background, medium shot. The most statistically probable composition.
- **What to look for**: Every image framed the same way. No unusual angles, crops, or perspectives.
- **Fix**: Specify unusual angles. "Shot from below," "extreme close-up of hands," "wide establishing shot with subject small in frame." The unexpected angle is the human signal.

### Clinical Cleanliness
No dust, no lens flare, no slight blur, no grain, no sensor noise, no chromatic aberration. AI images are clinically clean because noise was the enemy during training.
- **What to look for**: Absence of any photographic imperfection.
- **Fix**: Add grain in post. Shoot through real glass. Use a vintage lens preset. Real photos are messy.

### Decontextualized Style
AI mimics the surface aesthetics of film photography, oil painting, or watercolor without understanding the cultural or technical context. "Shot on film" produces digital perfection with a color grade, not actual film characteristics.
- **What to look for**: Style that's referenced but not understood. "Oil painting" that has no brushstroke variation. "Film photography" with no grain structure.

## Detection Techniques

### For Your Own Content
1. **The squint test**: Squint at the image. Does it feel "too perfect"? Does every element resolve cleanly?
2. **The detail test**: Zoom to 200%. Check skin texture, hair strands, hands, text, jewelry, background details.
3. **The context test**: Does this image tell a story? Could you describe the moment it was taken? If not, it feels AI.
4. **The metadata test**: AI images have different EXIF data than camera photos. Check for generation metadata.

### For Others' Content
1. Check hands, text, and accessories first — fastest tells.
2. Look at skin texture at full resolution.
3. Check if multiple images of the "same person" are consistent (AI struggles with character consistency across images).
4. Look at backgrounds — AI backgrounds often have subtle morphing, impossible architecture, or repeating patterns.

## What Good Image Usage Looks Like

1. **Real photos first.** A mediocre real photo beats a perfect AI photo for authenticity.
2. **If using AI generation**: Heavy post-processing to add imperfection. Crop aggressively. Add grain. Desaturate. Treat the AI output as a starting point, not a final product.
3. **Illustration over fake photography.** If you need visuals and don't have real photos, use intentional illustration (hand-drawn, vector, or stylized) rather than fake-realistic AI photos. Nobody questions an illustration's authenticity.
4. **Screenshots and screen recordings.** For product marketing, real UI screenshots beat any generated imagery.
5. **Process photos.** Behind-the-scenes, whiteboard shots, messy desk photos — the less polished, the more authentic.
