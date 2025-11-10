import { useMemo } from "react";

import {
  EquipmentArmor,
  EquipmentPack,
  EquipmentWeapon,
  ProficiencyStepPayload
} from "../../types";

export type EquipmentStepPayload = {
  weapons?: string[];
  armor?: string[];
  packs?: string[];
  custom_items?: Array<{ name: string; description?: string }>;
  currency?: Record<string, number>;
};

type EquipmentStepProps = {
  weapons: EquipmentWeapon[];
  armor: EquipmentArmor[];
  packs: EquipmentPack[];
  currencyTypes: string[];
  initialValues?: EquipmentStepPayload;
  onChange: (payload: EquipmentStepPayload) => void;
  disabled?: boolean;
};

function EquipmentStep({
  weapons,
  armor,
  packs,
  currencyTypes,
  initialValues,
  onChange,
  disabled = false
}: EquipmentStepProps): JSX.Element {
  const selectedWeapons = initialValues?.weapons ?? [];
  const selectedArmor = initialValues?.armor ?? [];
  const selectedPacks = initialValues?.packs ?? [];
  const currency = initialValues?.currency ?? {};

  const toggleSelection = (list: string[], value: string): string[] => {
    const set = new Set(list);
    if (set.has(value)) {
      set.delete(value);
    } else {
      set.add(value);
    }
    return Array.from(set);
  };

  const handleWeaponToggle = (value: string) => {
    onChange({
      ...initialValues,
      weapons: toggleSelection(selectedWeapons, value)
    });
  };

  const handleArmorToggle = (value: string) => {
    onChange({
      ...initialValues,
      armor: toggleSelection(selectedArmor, value)
    });
  };

  const handlePackToggle = (value: string) => {
    onChange({
      ...initialValues,
      packs: toggleSelection(selectedPacks, value)
    });
  };

  const handleCurrencyChange = (coin: string, amount: number) => {
    const updated = { ...currency, [coin]: amount };
    onChange({
      ...initialValues,
      currency: updated
    });
  };

  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Equipment & Currency</h2>
        <p className="text-sm text-gray-600">
          Choose your starting gear and note the amount of coin you have at the beginning of the campaign. You can add
          custom items later on the character sheet.
        </p>
      </header>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-arcane-blue">Weapons</h3>
        <div className="flex flex-wrap gap-2">
          {weapons.map((weapon) => {
            const selected = selectedWeapons.includes(weapon.id);
            return (
              <button
                key={weapon.id}
                className={`rounded border px-3 py-1 text-xs ${selected ? "border-arcane-blue bg-arcane-blue text-white" : "border-arcane-blue/30"}`}
                onClick={() => handleWeaponToggle(weapon.id)}
                type="button"
                disabled={disabled}
              >
                {weapon.name} ({weapon.damage})
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-arcane-blue">Armor</h3>
        <div className="flex flex-wrap gap-2">
          {armor.map((piece) => {
            const selected = selectedArmor.includes(piece.id);
            return (
              <button
                key={piece.id}
                className={`rounded border px-3 py-1 text-xs ${selected ? "border-forest-green bg-forest-green text-white" : "border-forest-green/30"}`}
                onClick={() => handleArmorToggle(piece.id)}
                type="button"
                disabled={disabled}
              >
                {piece.name} (AC {piece.ac})
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-arcane-blue">Equipment Packs</h3>
        <div className="flex flex-wrap gap-2">
          {packs.map((pack) => {
            const selected = selectedPacks.includes(pack.id);
            return (
              <button
                key={pack.id}
                className={`rounded border px-3 py-1 text-xs ${selected ? "border-amber-500 bg-amber-200" : "border-amber-500/30"}`}
                onClick={() => handlePackToggle(pack.id)}
                type="button"
                disabled={disabled}
              >
                {pack.name}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-arcane-blue">Currency</h3>
        <div className="mt-2 grid gap-2 sm:grid-cols-2 md:grid-cols-3">
          {currencyTypes.map((coin) => (
            <label key={coin} className="flex items-center gap-2 text-xs text-gray-600">
              <span className="w-12 uppercase text-arcane-blue">{coin}</span>
              <input
                className="flex-1 rounded border border-gray-300 px-2 py-1 text-sm focus:border-arcane-blue focus:outline-none"
                type="number"
                min={0}
                value={currency[coin] ?? 0}
                onChange={(event) => handleCurrencyChange(coin, Number(event.target.value))}
                disabled={disabled}
              />
            </label>
          ))}
        </div>
      </div>
    </section>
  );
}

export default EquipmentStep;
