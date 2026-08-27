# Design/UI Slop Patterns

Visual and structural patterns that make UI instantly recognizable as AI-generated. Each pattern includes detection criteria, the "why this?" test, and what to do instead.

## The Core Problem: Distributional Convergence

Every AI design tool (v0, Lovable, Bolt, Cursor) generates from the same training distribution. The output converges toward the statistical mean: same fonts, same colors, same layouts, same component styling. A fintech dashboard is indistinguishable from a CRM is indistinguishable from a project management tool. AI slop sites record conversion rates 91% lower than quality inventory.

## The 14 Patterns

### 1. Purple Gradient Disease
Dark background + neon purple/blue glowing gradients. The official color scheme of "we used AI." Tailwind ships rich indigo/violet families as defaults, and AI tools trained on these patterns reproduce them endlessly.
- **Detection**: Purple/blue gradients used decoratively without brand justification
- **The test**: "Is this purple because the brand IS purple, or because AI defaulted to it?"
- **Fix**: Colors come from brand palette. If the brand isn't about AI/tech/crypto, purple gradients are slop. Even if it IS tech, consider whether purple is a deliberate choice or a default.

### 2. The Default Layout (Sidebar + Topbar)
Logo top-left, sidebar with 6 nav items, top bar with search + avatar. The Salesforce layout from 2015. Every AI-generated dashboard uses this because it's the most common pattern in training data.
- **Detection**: This layout without questioning whether it serves the use case
- **The test**: "Is a persistent sidebar the right navigation for THIS app? Or did we just... not think about it?"
- **Alternatives**: Command palette (Raycast), floating contextual nav, tab bar, full-screen sections, typography-as-navigation, bottom bar, drawer nav

### 3. Bento Box Abuse
Apple-style grid of rounded cards used as a content dump. AI generates these because grids are mathematically simple and look "designed."
- **Detection**: Grid of equal-sized cards where content importance varies wildly
- **The test**: "Does every card deserve equal visual weight? What's the ONE thing on this page?"
- **Fix**: Use hierarchy. One hero element, supporting elements smaller. Not everything needs a card. Flat content with dividers. Asymmetric grid with one large + several small.

### 4. Shadow Soup
Every component has a different shadow depth, blur radius, and border treatment. Cards, buttons, and inputs all look like they're from different apps.
- **Detection**: More than 2 shadow values on a single page. Mix of bordered and shadowed cards.
- **The test**: "Do these shadows follow a consistent elevation system?"
- **Fix**: ONE approach: borders OR shadows. ONE system: rest state, hover state, active state. That's it.

### 5. Stock Illustration Disease
People carrying oversized objects. 3D metallic blobs. Gradient mesh backgrounds with no purpose. Abstract illustrations that communicate nothing about the brand.
- **Detection**: Decorative imagery that works for any product
- **The test**: "What does this illustration tell you about OUR product that text doesn't?"
- **Fix**: Show real UI, real data, real screenshots. Or use no imagery — let typography carry. Custom illustrations that reference the brand's visual language.

### 6. Unchanged Component Libraries
Using shadcn/ui, Material UI, or Chakra with zero customization. The same rounded-md buttons, the same gray-200 borders, the same slate color palette out of the box.
- **Detection**: Components identical to library defaults. Someone can name your UI library by looking at your app.
- **The test**: "Have we made this ours, or are we wearing someone else's clothes?"
- **Fix**: Every component customized to the brand. Different border radius, different color, different hover behavior, different font — SOMETHING that makes it not-default.

### 7. The Feature Grid
3-column grid of features, each with an icon + heading + one-sentence description. The homepage formula since 2018.
- **Detection**: Features as equal-weight grid items
- **The test**: "Is this the best way to show what our product does? Or just the easiest?"
- **Fix**: Tell a story. Show the product in action. One feature at a time, full-bleed. Before/after. Interactive demo. Anything except the grid.

### 8. Inter/System Font Default
AI tools default to Inter, Roboto, Arial, or system-ui. These are the typographic equivalent of lorem ipsum — they signal no design decision was made.
- **Detection**: Using these fonts without brand justification
- **The test**: "Did we CHOOSE this font, or did we just not change it?"
- **Fix**: Choose a typeface that reflects the brand. Distinctive serif for editorial. Monospace for technical. Bold geometric for playful. The font IS the personality.

### 9. Uniform Border Radius
16px (rounded-2xl) on everything. Cards, buttons, inputs, modals, badges — all the same radius. AI applies one radius value globally because it's safe.
- **Detection**: Same border radius on all elements regardless of size or function
- **The test**: "Should a 32px badge and a 400px card really have the same corner radius?"
- **Fix**: Radius should be proportional to element size and semantic to element type. Buttons can be pill-shaped while cards are slightly rounded while badges are fully round. Or go sharp: 0px radius is a statement.

### 10. Glassmorphism Without Purpose
Frosted glass cards floating in voids of soft pastel. Backdrop-blur on everything. Used because it looks "modern" without serving any function.
- **Detection**: backdrop-blur, translucent backgrounds used decoratively
- **The test**: "Is the translucency showing something behind the card that matters? Or is it just... there?"
- **Fix**: Glassmorphism makes sense when layering matters (a panel over live content). If the background is static, use a solid color.

### 11. Gradient Blob Decorations
Soft, blobby, multicolor gradients floating behind content. Purely ornamental shapes in corners and backgrounds.
- **Detection**: Abstract gradient shapes with no semantic meaning
- **The test**: "What happens if I delete these blobs?" If nothing is lost, delete them.
- **Fix**: Backgrounds should either be solid (the content does the work) or meaningful (a texture that reinforces the brand, data visualization, a real photograph).

### 12. Excessive Whitespace (The Middle)
Generous but purposeless spacing. Everything floats in a sea of space — not the confident white space of editorial design, just unused pixels.
- **Detection**: All elements have similar, generous spacing. No contrast between dense and spacious sections.
- **The test**: "Is this space deliberate (editorial, breathing room) or just unfilled?"
- **Fix**: Commit to either editorial white space (vast, intentional, with contrast) or controlled density (every pixel earns its place). The mushy middle signals no decision was made.

### 13. Dark Mode as Default
Dark mode because "it looks techy" without considering whether the brand or use case justifies it. AI defaults to dark because it's visually impressive in screenshots.
- **Detection**: Dark background without brand justification
- **The test**: "Is our audience using this at 2am in a dark room, or at 10am in an office?"
- **Fix**: Light mode is the right default for most products. Dark mode should be offered as an option, not a default, unless the brand identity specifically calls for it.

### 14. Missing States
Beautiful happy-path screens. But no empty states, no error states, no loading states, no edge cases.
- **Detection**: Only the "data exists and everything works" state is designed
- **The test**: "What does a brand-new user with zero data see?"
- **Fix**: Empty, error, loading, and edge states designed FIRST. These states are where personality lives.

## The Design Slop Checklist

Before shipping any screen, verify:
- [ ] Color palette is brand-specific, not Tailwind/AI defaults
- [ ] Font choice is deliberate, not Inter/Roboto/system
- [ ] Layout has been questioned — not sidebar+topbar by default
- [ ] Components are customized, not library defaults
- [ ] Shadow/border approach is consistent (ONE system)
- [ ] Border radius varies by element type and size
- [ ] Decorative elements serve the brand (or are removed)
- [ ] Spacing has contrast (dense + spacious, not uniform)
- [ ] All states designed: empty, error, loading, edge cases
- [ ] A screenshot alone communicates which brand this is
