import { FormEvent, useEffect, useState } from "react";

import { useUpdateGameState } from "../../hooks/useGameState";
import { GameState } from "../../types";

type GameStateEditorProps = {
  campaignId: number;
  gameState?: GameState;
};

function GameStateEditor({ campaignId, gameState }: GameStateEditorProps): JSX.Element {
  const [location, setLocation] = useState("");
  const [summary, setSummary] = useState("");
  const [questsText, setQuestsText] = useState("");
  const updateGameState = useUpdateGameState(campaignId);

  useEffect(() => {
    if (gameState) {
      setLocation(gameState.location ?? "");
      setSummary(gameState.summary ?? "");
      setQuestsText((gameState.active_quests ?? []).join("\n"));
    }
  }, [gameState]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const active_quests = questsText
      .split("\n")
      .map((quest) => quest.trim())
      .filter(Boolean);

    updateGameState.mutate({
      location: location || null,
      summary: summary || null,
      active_quests
    });
  };

  return (
    <section className="rounded-lg border border-arcane-blue/40 bg-white/80 p-4 shadow">
      <header className="mb-3">
        <h2 className="text-lg font-semibold text-arcane-blue">World State</h2>
        <p className="text-xs text-gray-600">
          Update the current location, quest log, and narrative summary as the adventure unfolds.
        </p>
      </header>

      <form className="space-y-3" onSubmit={handleSubmit}>
        <label className="block text-sm font-semibold text-arcane-blue">
          Location
          <input
            className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
            placeholder="Neverwinter Docks"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
          />
        </label>

        <label className="block text-sm font-semibold text-arcane-blue">
          Summary
          <textarea
            className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
            placeholder="The party negotiates with Captain Mira while storms gather on the horizon..."
            rows={3}
            value={summary}
            onChange={(event) => setSummary(event.target.value)}
          />
        </label>

        <label className="block text-sm font-semibold text-arcane-blue">
          Active Quests
          <textarea
            className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
            placeholder={"Retrieve the lost relic\nEscort the caravan"}
            rows={4}
            value={questsText}
            onChange={(event) => setQuestsText(event.target.value)}
          />
          <span className="mt-1 block text-xs text-gray-500">One quest per line.</span>
        </label>

        <button
          className="w-full rounded bg-forest-green px-4 py-2 text-sm font-semibold text-white hover:bg-forest-green/90 disabled:opacity-50"
          disabled={updateGameState.isPending}
          type="submit"
        >
          {updateGameState.isPending ? "Saving..." : "Save World State"}
        </button>
        {updateGameState.isError ? (
          <p className="text-xs text-ember-red">Unable to update game state. Please try again.</p>
        ) : null}
        {updateGameState.isSuccess ? (
          <p className="text-xs text-forest-green">World state updated.</p>
        ) : null}
      </form>
    </section>
  );
}

export default GameStateEditor;

