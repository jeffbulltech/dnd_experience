import { FormEvent, useMemo, useState } from "react";

import { useDiceHistory, useRollDice } from "../../hooks/useDice";
import { DiceRollLog } from "../../types";

const PRESET_EXPRESSIONS = ["d20", "2d20kh1", "d20+5", "4d6dl1", "2d6+3", "d100"];

type DiceRollerProps = {
  campaignId?: number;
  characterId?: number;
};

function DiceRoller({ campaignId, characterId }: DiceRollerProps): JSX.Element {
  const [expression, setExpression] = useState("d20");
  const [localHistory, setLocalHistory] = useState<DiceRollLog[]>([]);

  const filters = useMemo(
    () => ({ campaignId, characterId, limit: 10 }),
    [campaignId, characterId]
  );
  const historyQuery = useDiceHistory(filters);
  const rollMutation = useRollDice(filters);

  const combinedHistory = useMemo(() => {
    const apiHistory = historyQuery.data ?? [];
    return [...localHistory, ...apiHistory].slice(0, filters.limit ?? 10);
  }, [localHistory, historyQuery.data, filters.limit]);

  const handleRoll = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!expression.trim()) return;

    try {
      const result = await rollMutation.mutateAsync({
        expression,
        campaign_id: campaignId,
        character_id: characterId,
        roller_type: "player"
      });
      setLocalHistory((prev) => [
        {
          id: crypto.randomUUID(),
          campaign_id: campaignId,
          character_id: characterId,
          roller_type: "player",
          expression: result.expression,
          total: result.total,
          detail: result.detail ?? {},
          metadata: {},
          created_at: result.timestamp ?? new Date().toISOString()
        },
        ...prev
      ]);
    } catch (error) {
      console.error("Failed to roll dice", error);
    }
  };

  return (
    <section className="parchment-card p-5">
      <header className="mb-4 flex items-center justify-between border-b-2 border-arcane-blue-800/30 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🎲</span>
          <h2 className="text-xl font-display font-bold text-arcane-blue-900">Dice Roller</h2>
        </div>
        <div className="flex flex-wrap gap-1">
          {PRESET_EXPRESSIONS.map((preset) => (
            <button
              key={preset}
              className="rounded-md border border-arcane-blue-600 bg-arcane-blue-50 px-2 py-1 text-xs font-display font-semibold text-arcane-blue-800 transition-colors hover:bg-arcane-blue-200 hover:border-arcane-blue-700"
              onClick={() => setExpression(preset)}
              type="button"
            >
              {preset}
            </button>
          ))}
        </div>
      </header>

      <form className="mb-4 flex gap-2" onSubmit={handleRoll}>
        <input
          className="fantasy-input flex-1"
          placeholder="2d6+3"
          value={expression}
          onChange={(event) => setExpression(event.target.value)}
        />
        <button
          className="fantasy-button bg-gradient-to-b from-ember-red-700 to-ember-red-900 hover:from-ember-red-600 hover:to-ember-red-800 disabled:opacity-50"
          disabled={rollMutation.isPending}
          type="submit"
        >
          {rollMutation.isPending ? "Rolling..." : "Roll"}
        </button>
      </form>

      <div className="scroll-container max-h-64 space-y-2">
        {historyQuery.isLoading && (
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <span>🔮</span>
            <p className="font-display">Consulting the dice spirits...</p>
          </div>
        )}
        {!historyQuery.isLoading && combinedHistory.length === 0 ? (
          <p className="text-sm font-display text-gray-600">No rolls recorded yet.</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {combinedHistory.map((entry) => (
              <li key={`${entry.created_at}-${entry.expression}`} className="rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-3 shadow-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-display font-bold text-arcane-blue-800">{entry.expression}</span>
                  <span className="text-xs font-medium uppercase text-gray-500">{new Date(entry.created_at).toLocaleTimeString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-800">Total: <span className="text-ember-red-700">{entry.total}</span></span>
                  {Array.isArray(entry.detail?.rolls) ? (
                    <span className="text-xs text-gray-600">Rolls: {(entry.detail?.rolls as number[]).join(", ")}</span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

export default DiceRoller;
