import { InventoryItem } from "../../types";

type InventoryPanelProps = {
  items?: InventoryItem[];
  isLoading?: boolean;
  onRemove?: (itemId: number) => void;
};

function InventoryPanel({ items = [], isLoading = false, onRemove }: InventoryPanelProps): JSX.Element {
  const totalWeight = items.reduce((sum, item) => sum + (item.weight ?? 0) * item.quantity, 0);

  return (
    <section className="parchment-card p-5">
      <header className="mb-4 flex items-center justify-between border-b-2 border-arcane-blue-800/30 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🎒</span>
          <h2 className="text-lg font-display font-bold text-arcane-blue-900">Inventory</h2>
        </div>
        <span className="rounded-md bg-arcane-blue-100 px-2 py-1 text-xs font-display font-semibold uppercase text-arcane-blue-800">
          {totalWeight.toFixed(1)} lb
        </span>
      </header>

      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-gray-700">
          <span>🔮</span>
          <p className="font-display">Packing your gear...</p>
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm font-display text-gray-700">Your pack is empty. Claim loot or add equipment to get started.</p>
      ) : (
        <ul className="scroll-container max-h-64 space-y-2 text-sm">
          {items.map((item) => (
            <li key={item.id} className="rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-3 shadow-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="font-display font-bold text-arcane-blue-900">{item.name}</span>
                <span className="rounded-md bg-arcane-blue-100 px-2 py-0.5 text-xs font-display font-semibold uppercase text-arcane-blue-800">
                  x{item.quantity}
                </span>
              </div>
              {item.description ? (
                <p className="mb-2 text-xs text-gray-600">{item.description}</p>
              ) : null}
              <div className="flex items-center justify-between text-xs">
                {item.weight ? (
                  <span className="font-medium text-gray-600">Weight: {(item.weight * item.quantity).toFixed(1)} lb</span>
                ) : (
                  <span />
                )}
                {onRemove ? (
                  <button
                    className="rounded-md border border-ember-red-600 bg-ember-red-50 px-2 py-1 text-xs font-display font-semibold text-ember-red-800 transition-colors hover:bg-ember-red-100"
                    onClick={() => onRemove(item.id)}
                    type="button"
                  >
                    Remove
                  </button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default InventoryPanel;
