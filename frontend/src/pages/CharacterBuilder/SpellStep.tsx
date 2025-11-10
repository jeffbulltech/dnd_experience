import { useMemo, useState } from "react";

import { SpellDefinition, SpellSlotProgression } from "../../types";

type SpellStepPayload = {
  known?: string[];
  prepared?: string[];
  cantrips?: string[];
};

type SpellStepProps = {
  classId?: string;
  characterLevel: number;
  spells: SpellDefinition[];
  spellSlots: Record<string, SpellSlotProgression[]>;
  initialValues?: SpellStepPayload;
  onChange: (payload: SpellStepPayload) => void;
  disabled?: boolean;
};

function SpellStep({
  classId,
  characterLevel,
  spells,
  spellSlots,
  initialValues,
  onChange,
  disabled = false,
}: SpellStepProps): JSX.Element {
  const [levelFilter, setLevelFilter] = useState<number | "all">("all");
  const knownSpells = initialValues?.known ?? [];
  const preparedSpells = initialValues?.prepared ?? [];
  const cantrips = initialValues?.cantrips ?? [];

  const filteredSpells = useMemo(() => {
    return spells.filter((spell) => {
      if (classId && !spell.classes.includes(classId)) return false;
      if (levelFilter !== "all" && spell.level !== levelFilter) return false;
      return true;
    });
  }, [spells, classId, levelFilter]);

  const toggleListEntry = (list: string[], value: string, limit?: number): string[] => {
    const set = new Set(list);
    if (set.has(value)) {
      set.delete(value);
    } else if (!limit || set.size < limit) {
      set.add(value);
    }
    return Array.from(set);
  };

  const handleKnownToggle = (spellId: string) => {
    onChange({
      known: toggleListEntry(knownSpells, spellId),
      prepared: preparedSpells,
      cantrips,
    });
  };

  const handlePreparedToggle = (spellId: string) => {
    onChange({
      known: knownSpells,
      prepared: toggleListEntry(preparedSpells, spellId),
      cantrips,
    });
  };

  const handleCantripToggle = (spellId: string) => {
    onChange({
      known: knownSpells,
      prepared: preparedSpells,
      cantrips: toggleListEntry(cantrips, spellId),
    });
  };

  const toggleHandlers = {
    0: handleCantripToggle,
    default: handleKnownToggle,
  } as const;

  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Spells</h2>
        <p className="text-sm text-gray-600">
          Select the spells you know or prepare at your current class level. Spell availability depends on your class
          spell list.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-xs uppercase text-gray-500">Level Filter:</span>
        <button
          className={`rounded border px-2 py-1 ${levelFilter === "all" ? "bg-arcane-blue text-white" : "border-arcane-blue/30"}`}
          onClick={() => setLevelFilter("all")}
          type="button"
        >
          All
        </button>
        {[0, 1, 2, 3, 4, 5].map((level) => (
          <button
            key={level}
            className={`rounded border px-2 py-1 ${levelFilter === level ? "bg-arcane-blue text-white" : "border-arcane-blue/30"}`}
            onClick={() => setLevelFilter(level)}
            type="button"
          >
            {level}
          </button>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {filteredSpells.map((spell) => {
          const isKnown = knownSpells.includes(spell.id);
          const isPrepared = preparedSpells.includes(spell.id);
          const isCantrip = cantrips.includes(spell.id);
          const toggle = spell.level === 0 ? handleCantripToggle : handleKnownToggle;

          return (
            <div key={spell.id} className="rounded border border-arcane-blue/30 bg-white/85 p-3 text-sm">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-arcane-blue">{spell.name}</h3>
                <span className="text-xs text-gray-600">Level {spell.level}</span>
              </div>
              <p className="text-xs text-gray-600">{spell.school}</p>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                <button
                  className={`rounded border px-2 py-1 ${isKnown ? "border-arcane-blue bg-arcane-blue text-white" : "border-arcane-blue/30"}`}
                  onClick={() => toggle(spell.id)}
                  type="button"
                  disabled={disabled}
                >
                  {spell.level === 0 ? "Known Cantrip" : "Known"}
                </button>
                {spell.level > 0 ? (
                  <button
                    className={`rounded border px-2 py-1 ${isPrepared ? "border-forest-green bg-forest-green text-white" : "border-forest-green/30"}`}
                    onClick={() => handlePreparedToggle(spell.id)}
                    type="button"
                    disabled={disabled}
                  >
                    Prepared
                  </button>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default SpellStep;
