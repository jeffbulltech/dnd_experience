import { FormEvent, useMemo, useState } from "react";

import { CombatState } from "../../types";

type CombatTrackerProps = {
  state?: CombatState;
  isLoading?: boolean;
  onAddParticipant?: (payload: {
    name: string;
    initiative: number;
    hit_points: number;
    max_hit_points: number;
    armor_class: number;
  }) => void;
  onUpdateParticipant?: (participantId: number, updates: { hit_points?: number }) => void;
  onRemoveParticipant?: (participantId: number) => void;
  disabled?: boolean;
};

function CombatTracker({
  state,
  isLoading = false,
  onAddParticipant,
  onUpdateParticipant,
  onRemoveParticipant,
  disabled = false
}: CombatTrackerProps): JSX.Element {
  const combatants = state ? Object.values(state.combatants) : [];
  const [name, setName] = useState("");
  const [initiative, setInitiative] = useState(0);
  const [hitPoints, setHitPoints] = useState(0);
  const [maxHitPoints, setMaxHitPoints] = useState(0);
  const [armorClass, setArmorClass] = useState(10);

  const sortedCombatants = useMemo(() => {
    if (!state) return combatants;
    const order = state.turn_order;
    return [...combatants].sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
  }, [combatants, state]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!onAddParticipant) return;
    onAddParticipant({ name, initiative, hit_points: hitPoints, max_hit_points: maxHitPoints, armor_class: armorClass });
    setName("");
    setInitiative(0);
    setHitPoints(0);
    setMaxHitPoints(0);
    setArmorClass(10);
  };

  return (
    <section className="rounded-lg border border-arcane-blue/30 bg-white/85 p-4 shadow">
      <header className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-arcane-blue">Combat Tracker</h2>
        <span className="text-xs uppercase text-gray-600">
          {state?.round_number ? `Round ${state.round_number}` : "No active combat"}
        </span>
      </header>
      {isLoading ? (
        <p className="text-sm text-gray-600">Calculating turn order...</p>
      ) : sortedCombatants.length === 0 ? (
        <p className="text-sm text-gray-600">No active encounter. Await the Dungeon Master&apos;s call to arms.</p>
      ) : (
        <ul className="space-y-2 text-sm text-gray-700">
          {sortedCombatants.map((combatant, index) => {
            const isActive = combatant.id === state?.active_combatant_id;
            const progress = Math.max(0, Math.min(100, (combatant.hit_points / combatant.max_hit_points) * 100));
            return (
              <li
                key={combatant.id}
                className={`rounded border ${
                  isActive ? "border-arcane-blue" : "border-gray-200"
                } bg-parchment/70 p-3 shadow-sm`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-arcane-blue">{combatant.name}</span>
                  <span className="text-xs font-medium uppercase text-gray-500">
                    Initiative {combatant.initiative}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs uppercase text-gray-500">HP</span>
                    <span className="text-xs text-gray-700">
                      {combatant.hit_points}/{combatant.max_hit_points}
                    </span>
                  </div>
                  <div className="mt-1 h-2 rounded bg-gray-200">
                    <div
                      className="h-full rounded bg-forest-green transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    <button
                      className="rounded border border-ember-red px-2 py-1 text-ember-red hover:bg-ember-red hover:text-white disabled:opacity-50"
                      disabled={!onUpdateParticipant || disabled}
                      onClick={() =>
                        onUpdateParticipant?.(combatant.id, {
                          hit_points: Math.max(0, combatant.hit_points - 1)
                        })
                      }
                      type="button"
                    >
                      -1 HP
                    </button>
                    <button
                      className="rounded border border-forest-green px-2 py-1 text-forest-green hover:bg-forest-green hover:text-white disabled:opacity-50"
                      disabled={!onUpdateParticipant || disabled}
                      onClick={() =>
                        onUpdateParticipant?.(combatant.id, {
                          hit_points: Math.min(combatant.max_hit_points, combatant.hit_points + 1)
                        })
                      }
                      type="button"
                    >
                      +1 HP
                    </button>
                    <button
                      className="ml-auto text-ember-red hover:underline disabled:opacity-50"
                      disabled={!onRemoveParticipant || disabled}
                      onClick={() => onRemoveParticipant?.(combatant.id)}
                      type="button"
                    >
                      Remove
                    </button>
                  </div>
                </div>
                {combatant.conditions.length > 0 ? (
                  <p className="mt-2 text-xs text-amber-700">Conditions: {combatant.conditions.join(", ")}</p>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}

      {onAddParticipant ? (
        <form className="mt-4 space-y-3 rounded border border-dashed border-arcane-blue/40 p-3" onSubmit={handleSubmit}>
          <h3 className="text-sm font-semibold text-arcane-blue">Add Participant</h3>
          <div className="grid grid-cols-2 gap-2">
            <label className="text-xs font-medium text-gray-600">
              Name
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
              />
            </label>
            <label className="text-xs font-medium text-gray-600">
              Initiative
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                value={initiative}
                onChange={(event) => setInitiative(Number(event.target.value))}
              />
            </label>
            <label className="text-xs font-medium text-gray-600">
              Current HP
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                value={hitPoints}
                onChange={(event) => setHitPoints(Number(event.target.value))}
              />
            </label>
            <label className="text-xs font-medium text-gray-600">
              Max HP
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                value={maxHitPoints}
                onChange={(event) => setMaxHitPoints(Number(event.target.value))}
              />
            </label>
            <label className="text-xs font-medium text-gray-600">
              Armor Class
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                value={armorClass}
                onChange={(event) => setArmorClass(Number(event.target.value))}
              />
            </label>
          </div>
          <button
            className="w-full rounded border border-arcane-blue px-3 py-2 text-sm font-medium text-arcane-blue hover:bg-arcane-blue hover:text-white disabled:opacity-50"
            disabled={disabled}
            type="submit"
          >
            Add to Encounter
          </button>
        </form>
      ) : null}
    </section>
  );
}

export default CombatTracker;
