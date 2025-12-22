import { FormEvent, useEffect, useMemo, useState } from "react";

import { useUpdateCharacter } from "../../hooks/useCharacters";
import { AbilityScores, Character } from "../../types";

type CharacterSheetProps = {
  character: Character;
};

const ABILITY_KEYS: Array<keyof AbilityScores> = [
  "strength",
  "dexterity",
  "constitution",
  "intelligence",
  "wisdom",
  "charisma"
];

function CharacterSheet({ character }: CharacterSheetProps): JSX.Element {
  const updateCharacter = useUpdateCharacter();
  const [isEditing, setEditing] = useState(false);
  const [background, setBackground] = useState(character.background ?? "");
  const [alignment, setAlignment] = useState(character.alignment ?? "");
  const [experience, setExperience] = useState<number>(character.experience_points ?? 0);
  const [notes, setNotes] = useState(character.notes ?? "");
  const [abilityScores, setAbilityScores] = useState<AbilityScores>(() => withDefaultAbilityScores(character));

  useEffect(() => {
    if (isEditing) return;
    setBackground(character.background ?? "");
    setAlignment(character.alignment ?? "");
    setExperience(character.experience_points ?? 0);
    setNotes(character.notes ?? "");
    setAbilityScores(withDefaultAbilityScores(character));
  }, [character, isEditing]);

  const derivedModifier = (score: number) => Math.floor((score - 10) / 2);

  const abilityList = useMemo(
    () =>
      ABILITY_KEYS.map((key) => ({
        key,
        label: key.slice(0, 3).toUpperCase(),
        score: abilityScores[key],
        modifier: derivedModifier(abilityScores[key])
      })),
    [abilityScores]
  );

  const handleAbilityChange = (key: keyof AbilityScores, value: number) => {
    setAbilityScores((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await updateCharacter.mutateAsync({
        id: character.id,
        updates: {
          background,
          alignment,
          experience_points: experience,
          notes,
          ability_scores: abilityScores
        }
      });
      setEditing(false);
    } catch (error) {
      console.error("Failed to update character", error);
    }
  };

  return (
    <section className="parchment-card p-5">
      <header className="mb-4 flex items-center justify-between border-b-2 border-arcane-blue-800/30 pb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🛡</span>
            <h2 className="text-2xl font-display font-bold text-arcane-blue-900">{character.name}</h2>
          </div>
          <p className="text-sm font-display font-medium text-gray-700">
            Level {character.level} {character.race} {character.character_class}
          </p>
        </div>
        <button
          className="fantasy-button text-xs px-3 py-1 disabled:opacity-50"
          disabled={updateCharacter.isPending}
          onClick={() => setEditing((prev) => !prev)}
          type="button"
        >
          {isEditing ? "Cancel" : "Edit"}
        </button>
      </header>

      {isEditing ? (
        <form className="space-y-4 text-sm text-gray-700" onSubmit={handleSubmit}>
          <div className="grid grid-cols-3 gap-3">
            {abilityList.map(({ key, label, score }) => (
              <label
                key={key}
                className="flex flex-col rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-3 text-center uppercase"
              >
                <span className="text-xs font-display font-bold text-arcane-blue-800">{label}</span>
                <input
                  className="fantasy-input mt-2 text-center text-sm"
                  type="number"
                  value={score}
                  onChange={(event) => handleAbilityChange(key, Number(event.target.value))}
                />
              </label>
            ))}
          </div>

          <label className="block">
            <span className="text-xs font-display font-semibold uppercase text-gray-600">Background</span>
            <textarea
              className="fantasy-input mt-2 w-full"
              rows={3}
              value={background}
              onChange={(event) => setBackground(event.target.value)}
            />
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-xs font-display font-semibold uppercase text-gray-600">Alignment</span>
              <input
                className="fantasy-input mt-2 w-full"
                value={alignment}
                onChange={(event) => setAlignment(event.target.value)}
                placeholder="Chaotic Good"
              />
            </label>
            <label className="block">
              <span className="text-xs font-display font-semibold uppercase text-gray-600">Experience Points</span>
              <input
                className="fantasy-input mt-2 w-full"
                type="number"
                value={experience}
                onChange={(event) => setExperience(Number(event.target.value))}
                min={0}
              />
            </label>
          </div>

          <label className="block">
            <span className="text-xs font-display font-semibold uppercase text-gray-600">Notes</span>
            <textarea
              className="fantasy-input mt-2 w-full"
              rows={3}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>

          {updateCharacter.isError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-2">
              <p className="text-xs font-medium text-ember-red-800">Failed to update character. Please try again.</p>
            </div>
          ) : null}
          {updateCharacter.isSuccess ? (
            <div className="rounded-md border-2 border-forest-green-600 bg-forest-green-50 p-2">
              <p className="text-xs font-medium text-forest-green-800">Character updated.</p>
            </div>
          ) : null}

          <button
            className="fantasy-button w-full bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800 disabled:opacity-50"
            disabled={updateCharacter.isPending}
            type="submit"
          >
            {updateCharacter.isPending ? "Saving..." : "Save Changes"}
          </button>
        </form>
      ) : (
        <div className="space-y-4 text-sm text-gray-700">
          <div className="grid grid-cols-3 gap-3">
            {abilityList.map(({ key, label, score, modifier }) => (
              <div
                key={key}
                className={`rounded-md border-2 ${stateClass(score)} bg-parchment-50/90 p-3 text-center uppercase shadow-sm`}
              >
                <span className="text-xs font-display font-bold text-arcane-blue-800">{label}</span>
                <p className="text-2xl font-display font-bold text-gray-900">{score}</p>
                <p className="text-xs font-semibold text-gray-600">{modifier >= 0 ? `+${modifier}` : modifier}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-3">
              <h3 className="text-xs font-display font-semibold uppercase text-gray-600">Alignment</h3>
              <p className="mt-1 font-medium">{character.alignment ?? "Unaligned"}</p>
            </div>
            <div className="rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-3">
              <h3 className="text-xs font-display font-semibold uppercase text-gray-600">Experience</h3>
              <p className="mt-1 font-medium">{character.experience_points ?? 0} XP</p>
            </div>
          </div>

          <div className="rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-3">
            <h3 className="text-xs font-display font-semibold uppercase text-gray-600">Background</h3>
            <p className="mt-1">{character.background ?? "Unknown origins"}</p>
          </div>

          {character.notes ? (
            <div className="rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-3">
              <h3 className="text-xs font-display font-semibold uppercase text-gray-600">Notes</h3>
              <p className="mt-1 whitespace-pre-wrap">{character.notes}</p>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

function stateClass(score: number): string {
  if (score >= 16) return "border-forest-green-600";
  if (score <= 8) return "border-ember-red-600";
  return "border-arcane-blue-200/50";
}

export default CharacterSheet;

function withDefaultAbilityScores(character: Character): AbilityScores {
  const scores = character.ability_scores ?? ({} as AbilityScores);
  return {
    strength: scores.strength ?? 10,
    dexterity: scores.dexterity ?? 10,
    constitution: scores.constitution ?? 10,
    intelligence: scores.intelligence ?? 10,
    wisdom: scores.wisdom ?? 10,
    charisma: scores.charisma ?? 10
  };
}
