import { useEffect, useMemo, useState } from "react";

import { CharacterDraftStepPayload } from "../../types";

type AbilityScoreStepProps = {
  initialScores?: CharacterDraftStepPayload;
  onChange: (payload: CharacterDraftStepPayload) => void;
  disabled?: boolean;
};

const DEFAULT_SCORES = {
  strength: 15,
  dexterity: 14,
  constitution: 13,
  intelligence: 12,
  wisdom: 10,
  charisma: 8
};

const METHODS: Array<{ value: CharacterDraftStepPayload["method"]; label: string }> = [
  { value: "standard_array", label: "Standard Array" },
  { value: "point_buy", label: "Point Buy" },
  { value: "manual", label: "Manual Entry" }
];

function AbilityScoreStep({ initialScores, onChange, disabled = false }: AbilityScoreStepProps): JSX.Element {
  const [method, setMethod] = useState<CharacterDraftStepPayload["method"]>(
    initialScores?.method ?? "standard_array"
  );
  const [scores, setScores] = useState<Record<string, number>>({
    ...DEFAULT_SCORES,
    ...(initialScores?.scores as Record<string, number> | undefined)
  });

  useEffect(() => {
    setMethod(initialScores?.method ?? "standard_array");
    setScores({
      ...DEFAULT_SCORES,
      ...(initialScores?.scores as Record<string, number> | undefined)
    });
  }, [initialScores?.method, JSON.stringify(initialScores?.scores)]);

  useEffect(() => {
    onChange({ method, scores });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [method, scores]);

  const modifiers = useMemo(() => {
    return Object.fromEntries(
      Object.entries(scores).map(([ability, value]) => [ability, Math.floor((value - 10) / 2)])
    ) as Record<string, number>;
  }, [scores]);

  const handleScoreChange = (ability: string, value: number) => {
    const updated = { ...scores, [ability]: value };
    setScores(updated);
  };

  const handleMethodChange = (value: CharacterDraftStepPayload["method"]) => {
    setMethod(value);
  };

  return (
    <section className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Ability Scores</h2>
        <p className="text-sm text-gray-600">
          Choose how you’d like to assign your six ability scores. You can adjust individual values as you go.
        </p>
      </header>

      <div className="flex flex-wrap gap-3">
        {METHODS.map((option) => (
          <button
            key={option.value}
            className={`rounded border px-3 py-1 text-sm ${
              method === option.value
                ? "border-arcane-blue bg-arcane-blue text-white"
                : "border-arcane-blue/40 text-arcane-blue hover:border-arcane-blue"
            }`}
            onClick={() => handleMethodChange(option.value)}
            type="button"
            disabled={disabled}
          >
            {option.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(scores).map(([ability, value]) => (
          <div key={ability} className="rounded border border-arcane-blue/30 bg-white/80 p-3">
            <label className="flex flex-col">
              <span className="text-sm font-semibold text-arcane-blue">{ability.toUpperCase()}</span>
              <input
                className="mt-1 rounded border border-gray-300 px-2 py-1 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                value={value}
                onChange={(event) => handleScoreChange(ability, Number(event.target.value))}
                min={method === "manual" ? 3 : method === "point_buy" ? 8 : 8}
                max={method === "manual" ? 18 : method === "point_buy" ? 15 : 15}
                disabled={disabled}
              />
            </label>
            <p className="mt-2 text-xs text-gray-600">Modifier: {modifiers[ability] >= 0 ? "+" : ""}{modifiers[ability]}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default AbilityScoreStep;

