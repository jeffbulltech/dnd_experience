export type AbilityScores = {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
};

export type Species = {
  id: string;
  name: string;
  speed: number;
  size: string;
  abilities?: Record<string, number>;
  languages?: string[];
  traits?: string[];
};

export type Background = {
  id: string;
  name: string;
  skills?: string[];
  tools?: string[];
  languages?: number;
  feature?: string;
};

export type ClassSummary = {
  id: string;
  name: string;
  hit_die: number;
  primary_abilities: string[];
  saving_throws: string[];
  spellcasting?: {
    ability: string;
  };
  skill_choices?: {
    count: number;
    options: string[];
  };
};

export type SkillDefinition = {
  id: string;
  name: string;
  ability: string;
};

export type ToolDefinition = {
  id: string;
  name: string;
};

export type Character = {
  id: number;
  name: string;
  level: number;
  race?: string;
  character_class?: string;
  background?: string;
  alignment?: string | null;
  experience_points?: number;
  user_id?: number;
  campaign_id?: number;
  ability_scores?: AbilityScores;
  skills?: Record<string, number>;
  attributes?: Record<string, unknown>;
  notes?: string | null;
};

export type CharacterDraft = {
  id: number;
  name?: string | null;
  status: "draft" | "in_progress" | "ready_for_finalize";
  current_step?: string | null;
  starting_level: number;
  allow_feats: boolean;
  updated_at: string;
  variant_flags?: Record<string, unknown>;
  step_data?: Record<string, unknown>;
  created_at?: string;
};

export type ProficiencyStepPayload = {
  skills: string[];
  tools?: string[];
  expertise?: string[];
};

export type CharacterDraftCreate = {
  name?: string | null;
  starting_level?: number;
  allow_feats?: boolean;
  variant_flags?: Record<string, unknown>;
};

export type CharacterDraftStepPayload = {
  method?: "standard_array" | "point_buy" | "manual";
  scores?: Partial<AbilityScores>;
  [key: string]: unknown;
};

export type CharacterDraftStepUpdate = {
  payload?: CharacterDraftStepPayload;
  mark_complete?: boolean;
};

export type ChatMessage = {
  id: string;
  role: "player" | "gm";
  content: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
};

export type ChatHistoryEntry = {
  id: number;
  campaign_id: number;
  character_id?: number | null;
  role: "player" | "gm" | "system";
  content: string;
  rag_context?: string[] | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
};

export type RAGCitation = {
  excerpt: string;
  source: string;
  chunk_id?: string;
  score?: number;
  metadata?: Record<string, unknown>;
};

export type Campaign = {
  id: number;
  name: string;
  description?: string | null;
  owner_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type GameState = {
  campaign_id: number;
  location?: string | null;
  active_quests: string[];
  summary?: string | null;
  metadata: Record<string, unknown>;
  updated_at: string;
};

export type InventoryItem = {
  id: number;
  character_id: number;
  name: string;
  quantity: number;
  weight?: number | null;
  description?: string | null;
  properties?: Record<string, unknown> | null;
};

export type DiceRollResult = {
  expression: string;
  total: number;
  individual_rolls: number[];
  has_advantage: boolean;
  has_disadvantage: boolean;
  is_critical_success: boolean;
  is_critical_failure: boolean;
  detail?: Record<string, unknown> | null;
  timestamp?: string | null;
};

export type DiceRollLog = {
  id: number;
  campaign_id?: number | null;
  character_id?: number | null;
  roller_type: string;
  expression: string;
  total: number;
  detail?: Record<string, unknown> | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
};

export type CombatantState = {
  id: number;
  name: string;
  initiative: number;
  hit_points: number;
  max_hit_points: number;
  armor_class: number;
  conditions: string[];
};

export type CombatState = {
  campaign_id: number;
  round_number: number;
  turn_order: number[];
  active_combatant_id: number | null;
  combatants: Record<number, CombatantState>;
  last_updated: string;
};

export type User = {
  id: number;
  email: string;
  username: string;
  display_name: string;
  created_at: string;
  updated_at: string;
};

export type EquipmentArmor = {
  id: string;
  name: string;
  type: string;
  ac: number;
  cost?: Record<string, number>;
};

export type EquipmentWeapon = {
  id: string;
  name: string;
  damage: string;
  type: string;
  properties?: string[];
};

export type EquipmentPack = {
  id: string;
  name: string;
  contents: Array<{ item: string; quantity: number }>;
};

export type SpellDefinition = {
  id: string;
  name: string;
  level: number;
  school: string;
  classes: string[];
  casting_time: string;
  range: string;
  duration: string;
  components: string[];
};

export type SpellSlotProgression = {
  level: number;
  slots: Record<string, number>;
};

export type SpellStepPayload = {
  known?: string[];
  prepared?: string[];
  cantrips?: string[];
};
