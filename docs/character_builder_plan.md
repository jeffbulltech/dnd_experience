# D&D 5E Character Builder Plan

This document captures the architecture and implementation plan for the full D&D 5th Edition character builder, referencing the official 2024 character creation guide and the provided fillable character sheet.

## 1. Rule Coverage & Data Inventory

### Core Inputs
- **Ability Score Generation**: Standard array, point buy, manual rolling (with validation).
- **Species (Race)**: Selection, ability score bonuses, traits, languages, size, speed.
- **Background**: Skill/tool proficiencies, equipment, languages, feature, traits/bonds/ideals/flaws.
- **Class & Subclass**: Hit dice, saving throws, class features by level, spellcasting progression, subclass features, class-specific choices (fighting styles, domains, invocations, metamagic, etc.).
- **Level Selection**: Initial level (start at 1; allow higher start with choice of subclass/ASI per rules).
- **Alignment & Personality**: Alignment, ideals, bonds, flaws, notes.
- **Languages**: Mandatory and optional (from background/species/class or player choice).
- **Skill & Tool Proficiencies**: Derived from species, background, class, additional choices (expertise for certain classes).
- **Equipment & Wealth**: Starting equipment packages or gold amount, inventory items (weapons, armor, gear), currency breakdown.
- **Spellcasting**: Known/prepared spells, spell slots, spell attack modifier, spell save DC, cantrips.
- **Derived Stats**: Ability modifiers, proficiency bonus, passive Perception (and other relevant passive scores), AC, initiative, speed, hit points, hit dice, death saves, spell save DC, spell attack bonus, passive investigation/insight if applicable.
- **Other Notes**: Features & traits section text, allies & organizations, additional equipment/custom items.

### Derived Data Mapping
- **Ability Modifiers**: `(score - 10) / 2` rounded down.
- **Proficiency Bonus**: `+2` at levels 1–4, +3 at 5–8, etc.
- **Saving Throws**: Base ability modifier + proficiency bonus if proficient.
- **Skill Bonuses**: Base ability modifier + proficiency bonus if proficient (+ double proficiency for expertise).
- **Passive Perception**: `10 + Perception bonus`.
- **Armor Class**: Base formula depending on armor equipped/species/class traits.
- **Spell Save DC**: `8 + proficiency bonus + relevant ability modifier`.
- **Spell Attack Bonus**: `proficiency bonus + relevant ability modifier`.
- **Hit Points**: Level 1 max HP per class; subsequent levels add average or rolled value + CON mod (assume average unless rolling support required).
- **Hit Dice**: Number of dice equal to level, die type per class.
- **Speed**: From species plus modifiers.
- **Equipment Weight & Carrying Capacity**: Optional stretch goal (use STR mod × 15).

## 2. Domain Model

### Primary Entities
- `Character`: Core record, ties to user, current level, summary info.
- `CharacterAbilityScores`: STR/DEX/CON/INT/WIS/CHA values plus method used.
- `CharacterProficiencies`: skills, tools, weapons, armor (with `is_expertise` flag).
- `CharacterLanguages`: flexible list.
- `CharacterFeatures`: features & traits (class, subclass, background, species).
- `CharacterInventoryItem`: equipment entries with quantity, weight, notes; tags for armor, weapon, gear.
- `CharacterSpells`: known/prepared spells per level, cantrips, special notes.
- `CharacterSpellcasting`: casting ability, spell save DC, spell attack bonus, slot progression.
- `CharacterPersonality`: alignment, ideals, bonds, flaws, background story.
- `CharacterHitPoints`: current, max, temp HP, hit dice tracking.
- `CharacterChoices`: record of choices made (e.g., fighting style selection).
- `CharacterNotes`: additional sections (allies, organizations, treasure, etc.).
- `CharacterExport`: metadata for PDF exports.

### Reference Catalogs
- `Class`, `Subclass`, `ClassFeature`, `ClassOption` (fighting style, patron, etc.).
- `Species`, `SpeciesTrait`.
- `Background`, `BackgroundFeature`.
- `Skill`, `Tool`, `Language`.
- `Equipment`, `Weapon`, `Armor`.
- `Spell`, `SpellList`.
- `Feat` (if we support optional rules).
- `AbilityScoreImprovement` mapping (levels where ASI or feat choices occur).

These catalogs can be populated from SRD/Basic Rules data via fixtures or initial migrations. Consider storing raw JSON for source data if needed for patch updates.

## 3. Backend Architecture

### Services
- **CharacterBuilderService**: orchestrates step-by-step creation, applies rules from catalog, persists draft updates.
- **RuleEngine**: reusable calculations for ability modifiers, proficiency, spell slots, etc.
- **CatalogService**: exposes catalog data for the frontend (classes, species, backgrounds, spells, equipment).
- **PDFGenerator**: fills the official fillable PDF with final character data.
- **ValidationService**: ensures selections comply with rules (point-buy totals, allowed skill choices, spell counts).

### API Endpoints (proposed)
- `GET /api/catalog/classes`, `/backgrounds`, `/species`, `/spells`, `/equipment`, etc.
- Builder workflow:
  - `POST /api/characters/drafts`: start new draft (optionally specify base settings).
  - `GET /api/characters/drafts/{id}`: fetch current draft state (for resume).
  - Step updates: `PATCH /api/characters/drafts/{id}/abilities`, `/origin`, `/class`, `/proficiencies`, `/equipment`, `/spells`, `/personality`, etc.
  - `POST /api/characters/drafts/{id}/finalize`: validate and convert to completed character.
  - `GET /api/characters/{id}/export/pdf`: download filled character sheet.
- Existing endpoints (list characters, etc.) should now include builder-complete data.

### Validation & Business Rules
- **Ability score methods**: enforce totals (point buy 27 points, standard array, etc.).
- **Skill selection**: limit based on class/species/background rules; prevent duplicates unless allowed.
- **Spell selection**: enforce known spells count, prepared slots, level restrictions.
- **Equipment**: ensure starting equipment packages align with class/background; allow custom additions.
- **Class features**: track options taken at specific levels (e.g., 1st-level fighting style, 2nd-level action surge tracking).
- **ASI/Feats**: handle optional rules (feats require enabling; otherwise ability score increase).

## 4. Frontend Builder Workflow

### Step Outline
1. **Welcome & Method**: choose ability score method, character start level, toggles (feats allowed, multiclass support if included).
2. **Ability Scores**: input based on method, display auto-calculated modifiers.
3. **Origin**: select species + traits overrides, background selection with skill/tool/language choices.
4. **Class & Level**:
   - Choose class, subclass (if starting above level 2), auto-calc hit points, spellcasting ability.
   - Present class features at level (choose class options where relevant).
5. **Proficiencies & Skills**: confirm skill/tool proficiencies from species/background/class, select extras and expertise options.
6. **Equipment & Wealth**: choose starting pack/weapons/armor/custom items; optionally accept recommended kit.
7. **Spells**: for casters, choose known/prepared spells, track slots, highlight requirements per level.
8. **Personality & Details**: alignment, ideals, bonds, flaws, trait text, allies, notes.
9. **Summary & Review**: display computed stats, derived fields, spell summary, equipment list, export options.

### UI Considerations
- Progress indicator with ability to navigate back (with warning if invalid).
- Inline rule helper cards (tooltips referencing official steps).
- Autosave after each step (call backend draft endpoints).
- Validation prompts and disabled “Next” when step incomplete.
- Support import of saved drafts (list builder drafts on landing page).

### State Management
- React context or Zustand store storing builder state.
- Use React Query to interact with backend draft APIs (fetch, update).
- Derived values computed both client-side for UX and validated server-side.

## 5. PDF Export Strategy

- Use backend service to load `5E_CharacterSheet_Fillable.pdf` and fill fields.
- Map each field (e.g., `CharacterName`, `PlayerName`, `STR`, `STRmod`, etc.) to data from finalized character.
- Generate PDF on demand and stream to client; optionally store a cached copy.
- Provide JSON export for backup/import.
- (Optional) Support printing an inventory/equipment supplement if the base PDF lacks space.

## 6. Testing & QA Plan

### Backend
- Unit tests for rule calculations (ability modifiers, proficiency bonus by level, ASI validation, spell slot progression).
- Integration tests covering example builds:
  - Level 1 Fighter (simple martial).
  - Level 1 Wizard (spellcasting).
  - Level 3 Rogue (expertise, subclass features).
  - Higher-level cleric or paladin to test spell and feature stacking.

### Frontend
- Component tests for each builder step: ensure validation, derived totals, navigation.
- End-to-end tests (Cypress/Playwright) to simulate entire builder flow.
- Snapshot tests for summary review screen.

### PDF
- Automated check verifying filled PDF fields match expected values (e.g., parse filled PDF text).
- Manual QA to confirm layout, fonts, and special fields (like checkbox for inspiration) render correctly.

### Regression
- Ensure existing character listing, editing, and inventory/dice integrations remain functional with expanded schema.

## 7. Implementation Roadmap

1. **Finalize catalogs**: load SRD data and seed reference tables (classes, spells, etc.).
2. **Database migrations**: introduce new character-centric tables.
3. **Builder API skeleton**: endpoints for drafts, catalog fetch.
4. **Rule engine services**: ability mod/proficiency/spell slot calculations.
5. **Frontend builder scaffolding**: wizard layout, ability score step, connect to draft API.
6. **Iterate steps**: add origin → class → skills → equipment → spells → personality.
7. **Summary & finalize**: final validation, creation of completed character entry.
8. **PDF export**: implement generator and download endpoint.
9. **Testing & QA**: automated tests + manual passes.

---

With this plan in place, we can proceed to implementation in phases, ensuring each step aligns with official rules and the provided character sheet template. Once the catalogs and schema are ready, we’ll start exposing the builder backend endpoints and building out the frontend wizard.***

