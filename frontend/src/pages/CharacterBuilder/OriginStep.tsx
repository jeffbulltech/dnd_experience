import { useMemo } from "react";

import { Background, CharacterDraftStepPayload, Species } from "../../types";

type OriginStepProps = {
  species: Species[];
  backgrounds: Background[];
  languages: string[];
  initialValues?: CharacterDraftStepPayload;
  onChange: (payload: CharacterDraftStepPayload) => void;
  disabled?: boolean;
};

function OriginStep({ species, backgrounds, languages, initialValues, onChange, disabled = false }: OriginStepProps) {
  const selectedSpecies = initialValues?.species as string | undefined;
  const selectedBackground = initialValues?.background as string | undefined;
  const bonusLanguages = (initialValues?.languages as string[]) ?? [];

  const speciesOptions = useMemo(() => species, [species]);
  const backgroundOptions = useMemo(() => backgrounds, [backgrounds]);

  const handleSpeciesChange = (value: string) => {
    onChange({
      ...(initialValues ?? {}),
      species: value
    });
  };

  const handleBackgroundChange = (value: string) => {
    onChange({
      ...(initialValues ?? {}),
      background: value
    });
  };

  const handleLanguageToggle = (value: string) => {
    const current = new Set(bonusLanguages);
    if (current.has(value)) {
      current.delete(value);
    } else {
      current.add(value);
    }
    onChange({
      ...(initialValues ?? {}),
      languages: Array.from(current)
    });
  };

  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Origin</h2>
        <p className="text-sm text-gray-600">
          Choose your characters species and background. These selections determine traits, proficiencies, and
          story hooks.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-arcane-blue">Species</h3>
          <div className="space-y-2">
            {speciesOptions.map((option) => (
              <button
                key={option.id}
                className={`w-full rounded border px-3 py-2 text-left text-sm transition ${
                  selectedSpecies === option.id
                    ? "border-arcane-blue bg-arcane-blue/10"
                    : "border-arcane-blue/20 hover:border-arcane-blue/60"
                }`}
                onClick={() => handleSpeciesChange(option.id)}
                type="button"
                disabled={disabled}
              >
                <span className="font-semibold text-arcane-blue">{option.name}</span>
                <p className="text-xs text-gray-600">Speed {option.speed} ft. • Size {option.size}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-arcane-blue">Background</h3>
          <div className="space-y-2">
            {backgroundOptions.map((background) => (
              <button
                key={background.id}
                className={`w-full rounded border px-3 py-2 text-left text-sm transition ${
                  selectedBackground === background.id
                    ? "border-forest-green bg-forest-green/10"
                    : "border-forest-green/20 hover:border-forest-green/60"
                }`}
                onClick={() => handleBackgroundChange(background.id)}
                type="button"
                disabled={disabled}
              >
                <span className="font-semibold text-forest-green">{background.name}</span>
                {background.feature ? (
                  <p className="text-xs text-gray-600">Feature: {background.feature}</p>
                ) : null}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-arcane-blue">Bonus Languages</h3>
        <p className="text-xs text-gray-600">Select additional languages granted by your origin.</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {languages.map((language) => {
            const selected = bonusLanguages.includes(language);
            return (
              <button
                key={language}
                className={`rounded border px-2 py-1 text-xs ${
                  selected ? "border-arcane-blue bg-arcane-blue text-white" : "border-arcane-blue/30"
                }`}
                onClick={() => handleLanguageToggle(language)}
                type="button"
                disabled={disabled}
              >
                {language}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default OriginStep;
