import { InventoryItem } from "../../types";

type InventoryPanelProps = {
  items?: InventoryItem[];
  isLoading?: boolean;
  onRemove?: (itemId: number) => void;
};

function InventoryPanel({ items = [], isLoading = false, onRemove }: InventoryPanelProps): JSX.Element {
  const totalWeight = items.reduce((sum, item) => sum + (item.weight ?? 0) * item.quantity, 0);

  return (
    <section className="rounded-lg border border-arcane-blue/30 bg-white/85 p-4 shadow">
      <header className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-arcane-blue">Inventory</h2>
        <span className="text-xs uppercase text-gray-600">{totalWeight.toFixed(1)} lb carried</span>
      </header>

      {isLoading ? (
        <p className="text-sm text-gray-600">Packing your gear...</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-600">Your pack is empty. Claim loot or add equipment to get started.</p>
      ) : (
        <ul className="space-y-2 text-sm text-gray-700">
          {items.map((item) => (
            <li key={item.id} className="rounded border border-gray-200 bg-parchment/60 p-2 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-arcane-blue">{item.name}</span>
                <span className="text-xs uppercase text-gray-500">x{item.quantity}</span>
              </div>
              {item.description ? <p className="text-xs text-gray-600">{item.description}</p> : null}
              <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                {item.weight ? <span>Weight: {(item.weight * item.quantity).toFixed(1)} lb</span> : <span />}
                {onRemove ? (
                  <button className="text-ember-red hover:underline" onClick={() => onRemove(item.id)} type="button">
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
