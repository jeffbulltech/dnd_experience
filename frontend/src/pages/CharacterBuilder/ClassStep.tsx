import { ClassSummary } from "../../types";

type ClassStepProps = {
  classes: ClassSummary[];
  initialValues?: { class?: string };
  onChange: (payload: { class: string }) => void;
  disabled?: boolean;
};

function ClassStep({ classes, initialValues, onChange, disabled = false }: ClassStepProps): JSX.Element {
  const selectedClass = initialValues?.class;

  return (
    <section className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Class</h2>
        <p className="text-sm text-gray-600">
          Pick the archetype that defines your heros abilities, hit points, and saving throws. Additional
          subclass and feature choices will unlock at higher levels.
        </p>
      </header>

      <div className="grid gap-3 md:grid-cols-2">
        {classes.map((klass) => (
          <button
            key={klass.id}
            className={`rounded border p-4 text-left transition ${
              selectedClass === klass.id
                ? "border-forest-green bg-forest-green/10"
                : "border-arcane-blue/20 hover:border-arcane-blue/60"
            }`}
            onClick={() => onChange({ class: klass.id })}
            type="button"
            disabled={disabled}
          >
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-forest-green">{klass.name}</span>
              <span className="text-xs text-gray-600">d{klass.hit_die} Hit Die</span>
            </div>
            <p className="mt-2 text-xs text-gray-600">
              Primary Abilities: {klass.primary_abilities.map((ability) => ability.toUpperCase()).join(", ")}
            </p>
            <p className="text-xs text-gray-600">
              Saving Throws: {klass.saving_throws.map((save) => save.toUpperCase()).join(", ")}
            </p>
            {klass.spellcasting ? (
              <p className="text-xs text-gray-600">
                Spellcasting Ability: {klass.spellcasting.ability.toUpperCase()}
              </p>
            ) : null}
          </button>
        ))}
      </div>
    </section>
  );
}

export default ClassStep;
