type QuestLogProps = {
  quests?: string[];
};

function QuestLog({ quests = [] }: QuestLogProps): JSX.Element {
  return (
    <section className="rounded-lg border border-arcane-blue/30 bg-white/85 p-4 shadow">
      <header className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-arcane-blue">Quest Log</h2>
        <span className="text-xs uppercase text-gray-600">{quests.length} objectives</span>
      </header>

      {quests.length === 0 ? (
        <p className="text-sm text-gray-600">No quests are currently tracked. Chronicle your deeds to begin.</p>
      ) : (
        <ul className="space-y-2 text-sm text-gray-700">
          {quests.map((quest, index) => (
            <li key={`${quest}-${index}`} className="rounded border border-gray-200 bg-parchment/60 p-2 shadow-sm">
              <span className="font-semibold text-arcane-blue">Objective {index + 1}</span>
              <p className="text-xs text-gray-600">{quest}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default QuestLog;
