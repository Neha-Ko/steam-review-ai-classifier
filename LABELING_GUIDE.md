# Labeling Guide (v4)

How to label negative Steam reviews for the project *Do Players Notice the AI, or Just the Quality?* The same rules are used for hand labels (the test set) and for the Claude prompt. Every review being labeled is a negative (thumbs-down) review.

**The test:** could two people who have never spoken give the same review the same label? Every rule below points to words you can see in the review, not to a guess about what the reviewer meant or what the developer actually did.

## What you fill in

| Column | Required? | Values |
|---|---|---|
| `reason` | Always | `GENAI`, `QUALITY`, `BOTH`, `OTHER`, `SKIP` |
| `unsure` | If unsure | `Y`, otherwise leave blank |
| `note` | Optional (required for `SKIP`) | A few words on why, for any hard call |

The `ai_target` column was dropped to fit the timeline; leave it blank.

## The labels

| Label | Use it when the review... | Anchor: what you'd see |
|---|---|---|
| `GENAI` | Complains about generative AI, and that is its only complaint | Names AI-made content or accuses the game of being AI-made: "AI art," "AI voices," "AI slop," "made with ChatGPT," "looks AI-generated," "Midjourney," or simply "uses AI generated art" |
| `QUALITY` | Complains about the game, without blaming generative AI | Bugs, crashes, performance, gameplay, content, difficulty, price, servers, updates, abandonment, **enemy or NPC "AI"**, art or voices called bad **without** naming AI |
| `BOTH` | Has a generative-AI complaint **and** at least one separate, non-AI quality complaint | One `GENAI` anchor plus one `QUALITY` anchor, e.g. "inventory is annoying, no stealth, and AI images" |
| `OTHER` | Gives no reason, or the reason isn't about the game | Empty of reasons ("no," ".", an emoji, ASCII art), jokes or memes, "refunded" with no reason, praise only, "not for me," politics or drama outside the game |
| `SKIP` | Is not in English, or its English part gives no reason | Spanish, Portuguese, German, etc.; write the language in `note` |

`GENAI + BOTH` = reviews with a generative-AI complaint. `QUALITY + BOTH` = reviews with a quality complaint. `SKIP` reviews are removed from the analysis.

## Decision steps (in order)

1. **Is the review in English, or does its English part state a reason?** If not → `SKIP`.
2. **Is there a stated reason about the game?** If not → `OTHER`.
3. **Does the review complain about generative AI?** Look for a `GENAI` anchor. If "AI" means enemies, NPCs, bots, companions or pathfinding, that is **not** generative AI. In a negative review, mentioning generative AI as a plain fact counts as a complaint. Any criticism of AI-made content counts, however mild, unless the reviewer explicitly says it isn't a problem.
4. **If yes:** is there also a separate complaint that stands on its own without the AI (it doesn't involve the AI-made content)? Yes → `BOTH`. No → `GENAI`.
5. **If no:** → `QUALITY`.

## Edge cases

Examples come only from the pilot (development set) or are written as illustrations, never copied from test reviews.

| Review says | Label | Rule |
|---|---|---|
| "stupid AI that just runs straight at you" | `QUALITY` | Enemy behavior is gameplay, not generative AI |
| "the AI mapping def blows too, random deer/racoon/wolves... ZOOMING through your base" | `QUALITY` | Animal pathfinding is game AI |
| "AI random gen skins" | `GENAI` | Label what the reviewer says, whether or not it's true |
| "uses AI generated art" (no other words) | `GENAI` | In a negative review, mentioning AI as a plain fact counts as the stated reason |
| "the art looks bad because it's AI" | `GENAI` | A problem blamed on generative AI is one AI complaint, not `BOTH` |
| "no stealth, hard to get ammo, and ai images" | `BOTH` | Generative-AI complaint plus separate, non-AI quality complaints |
| "the devs asked chatGPT to make a zombie survival game, but terrible" | `GENAI` or `BOTH` | An accusation used as an insult still counts as a generative-AI complaint; `BOTH` if other complaints appear |
| "Too bad all they wish to churn out is slop" (AI never named) | `QUALITY` | "Slop" alone is generic slang; it counts only when AI is named or clearly implied |
| "soulless," "asset flip," "cash grab," "generic" (no AI named) | `QUALITY` | Not generative AI unless AI is named |
| "the voice acting is terrible" | `QUALITY` | Voices called bad without naming AI |
| "the AI voices are terrible" | `GENAI` | AI named |
| "I don't mind the AI art, but it crashes constantly" | `QUALITY` | AI mentioned, but explicitly not a complaint |
| "store page uses AI images, misleading" | `GENAI` | Complaint about AI in marketing |
| "the trailer is obviously AI" | `GENAI` | AI in trailers, store pages, or marketing counts; it's part of the product being sold |
| "wouldn't be surprised if the whole game is AI" | `GENAI` | Speculation or suspicion of AI use counts as an accusation |
| "like others said, the AI voices are awful" | `GENAI` | The reviewer agrees, so it's their complaint |
| "reviews say it's AI, I didn't notice; it's just buggy" | `QUALITY` | Label only the reviewer's own complaints |
| Only reports that others complain about AI, without taking a side | Best label + `unsure` | Discussed when settling disagreements |
| "abandoned," "no updates," "devs disappeared" | `QUALITY` | Lack of updates or support is a complaint about the product |
| Sarcasm ("great, another masterpiece of AI art") | Label the meaning | Here: `GENAI` |
| "crashes" (one word) | `QUALITY` | A short review with a reason still counts |
| Review mixes praise and complaints | Label the complaints | Ignore the praise |
| "the AI voices are mostly fine, but sometimes sound really jarring" | `GENAI` (or `BOTH`) | Any criticism of AI-made content counts, however mild |
| "some dialogue sounds like placeholder AI, but that shouldn't count against it" | Label the rest of the review | AI noticed but explicitly excused; not a complaint |
| "some AI was used, but I play with the sound off anyway" | Label the rest of the review | AI mentioned with a reason it doesn't matter; not a complaint |
| "won't support AI voice acting, it takes actors' jobs" | `GENAI` | An ethical objection to AI use counts |
| Checkbox template with "AI Bot" checked for story | `GENAI` (or `BOTH`) | Choosing an AI option as a rating counts as a generative-AI criticism |
| Mocks AI-voiced characters for what they say, with no other complaint | `GENAI` | `BOTH` requires a separate complaint that doesn't involve the AI-made content |
| "an AI-generated mess with no content" | `BOTH` | "No content" is a separate complaint that would apply without AI |
| "fun, but it's a copy of another game; buy that one instead" (plus an AI complaint) | `BOTH` | Being a copy of another game is a quality complaint, like "generic" |
| Only praise, no complaint (thumbs-down anyway) | `OTHER` | No stated reason; likely a misclick. Note "praise only" |
| "good game, just not for me" | `OTHER` | Personal preference, not a problem with the game |
| Complains the game's story or themes are too political or preachy | `QUALITY` | A complaint about the game's own content; `OTHER` is only for politics or drama outside the game |
| Review in two languages, with English text stating a reason | Label from the English part | If the English part has no reason, `SKIP` |
| Review entirely in Spanish, German, etc. | `SKIP` | Write the language in `note` |

## When unsure

Pick the best label, mark `unsure` = `Y`, and write a short `note`. Unsure reviews are discussed when settling disagreements, and new edge cases are added to this guide.

## Labeling rules

- Label blind: don't look up the game, its group, or whether the keywords flagged it.
- Don't change a label after seeing Claude's output.
- Label in short sittings (about 50 reviews) to stay consistent.

## Change log

- **v1:** First version, built from the pilot hand check.
- **v2:** Dropped `ai_target` to fit the timeline. Added `SKIP` for non-English reviews. Added rules from labeling: plain mentions of AI count as complaints, problems blamed on AI are `GENAI` (not `BOTH`), abandoned games are `QUALITY`, label only the reviewer's own complaints, and mixed-language reviews are labeled from the English part.
- **v3:** Added rules for AI in trailers or marketing, and for speculating that a game is AI-made.
- **v4:** Added rules from labeling and settling disagreements: mild criticism of AI content counts, explicitly excused AI doesn't, ethical objections count, "AI Bot" checkbox ratings count, `BOTH` needs a complaint that stands without the AI, copies of other games and political story content are `QUALITY`, and praise-only or "not for me" reviews are `OTHER`.
