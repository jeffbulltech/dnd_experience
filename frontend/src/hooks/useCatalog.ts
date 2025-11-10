import { useQuery } from "@tanstack/react-query";

import { api } from "../services/api";
import {
  Background,
  ClassSummary,
  Species,
  SkillDefinition,
  ToolDefinition,
  EquipmentArmor,
  EquipmentWeapon,
  EquipmentPack,
  SpellDefinition,
  SpellSlotProgression
} from "../types";

type CatalogData = {
  species: Species[];
  backgrounds: Background[];
  classes: ClassSummary[];
  skills: SkillDefinition[];
  tools: ToolDefinition[];
  armor: EquipmentArmor[];
  weapons: EquipmentWeapon[];
  packs: EquipmentPack[];
  currency: string[];
  languages: string[];
  spells: SpellDefinition[];
  spellSlots: Record<string, SpellSlotProgression[]>;
};

async function fetchCatalog(): Promise<CatalogData> {
  const [
    species,
    backgrounds,
    classes,
    skills,
    tools,
    armor,
    weapons,
    packs,
    currency,
    languages,
    spells,
    spellSlots,
  ] = await Promise.all([
    api.get<Species[]>("/catalog/species"),
    api.get<Background[]>("/catalog/backgrounds"),
    api.get<ClassSummary[]>("/catalog/classes"),
    api.get<SkillDefinition[]>("/catalog/skills"),
    api.get<ToolDefinition[]>("/catalog/tools"),
    api.get<EquipmentArmor[]>("/catalog/armor"),
    api.get<EquipmentWeapon[]>("/catalog/weapons"),
    api.get<EquipmentPack[]>("/catalog/equipment-packs"),
    api.get<string[]>("/catalog/currency"),
    api.get<string[]>("/catalog/languages"),
    api.get<SpellDefinition[]>("/catalog/spells"),
    api.get<Record<string, SpellSlotProgression[]>>("/catalog/spell-slots"),
  ]);

  return {
    species: species.data,
    backgrounds: backgrounds.data,
    classes: classes.data,
    skills: skills.data,
    tools: tools.data,
    armor: armor.data,
    weapons: weapons.data,
    packs: packs.data,
    currency: currency.data,
    languages: languages.data,
    spells: spells.data,
    spellSlots: spellSlots.data,
  };
}

export function useCatalog() {
  return useQuery({
    queryKey: ["catalog"],
    queryFn: fetchCatalog,
    staleTime: 1000 * 60 * 60 // 1 hour
  });
}
