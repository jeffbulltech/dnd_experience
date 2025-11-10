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
    <section className="rounded-lg border border-arcane-blue/30 bg-white/85 p-4 shadow">
      <header className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-arcane-blue">Dice Roller</h2>
        <div className="flex gap-2">
          {PRESET_EXPRESSIONS.map((preset) => (
            <button
              key={preset}
              className="rounded border border-arcane-blue px-2 py-1 text-xs text-arcane-blue hover:bg-arcane-blue hover:text-white"
              onClick={() => setExpression(preset)}
              type="button"
            >
              {preset}
            </button>
          ))}
        </div>
      </header>

      <form className="flex gap-2" onSubmit={handleRoll}>
        <input
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-arcane-blue focus:outline-none"
          placeholder="2d6+3"
          value={expression}
          onChange={(event) => setExpression(event.target.value)}
        />
        <button
          className="rounded bg-ember-red px-4 py-2 text-sm font-semibold text-white hover:bg-ember-red/90 disabled:opacity-50"
          disabled={rollMutation.isPending}
          type="submit"
        >
          {rollMutation.isPending ? "Rolling..." : "Roll"}
        </button>
      </form>

      <div className="mt-4 space-y-2">
        {historyQuery.isLoading && <p className="text-sm text-gray-600">Consulting the dice spirits...</p>}
        {!historyQuery.isLoading && combinedHistory.length === 0 ? (
          <p className="text-sm text-gray-600">No rolls recorded yet.</p>
        ) : (
          <ul className="space-y-2 text-sm text-gray-700">
            {combinedHistory.map((entry) => (
              <li key={`${entry.created_at}-${entry.expression}`} className="rounded border border-gray-200 bg-parchment/60 p-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-arcane-blue">{entry.expression}</span>
                  <span className="text-xs uppercase text-gray-500">{new Date(entry.created_at).toLocaleTimeString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Total: {entry.total}</span>
                  {Array.isArray(entry.detail?.rolls) ? (
                    <span>Rolls: {(entry.detail?.rolls as number[]).join(", ")}</span>
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
