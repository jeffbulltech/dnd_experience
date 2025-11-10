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
    <section className="rounded-lg border border-arcane-blue/30 bg-white/85 p-4 shadow">
      <header className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-serif text-arcane-blue">{character.name}</h2>
          <p className="text-sm text-gray-700">
            Level {character.level} {character.race} {character.character_class}
          </p>
        </div>
        <button
          className="rounded border border-arcane-blue px-3 py-1 text-xs uppercase text-arcane-blue hover:bg-arcane-blue hover:text-white disabled:opacity-50"
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
                className="flex flex-col rounded border border-gray-200 bg-parchment/60 p-3 text-center uppercase"
              >
                <span className="text-xs font-semibold text-arcane-blue">{label}</span>
                <input
                  className="mt-2 rounded border border-gray-300 p-1 text-sm focus:border-arcane-blue focus:outline-none"
                  type="number"
                  value={score}
                  onChange={(event) => handleAbilityChange(key, Number(event.target.value))}
                />
              </label>
            ))}
          </div>

          <label className="block">
            <span className="text-xs font-semibold uppercase text-gray-500">Background</span>
            <textarea
              className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
              rows={3}
              value={background}
              onChange={(event) => setBackground(event.target.value)}
            />
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-xs font-semibold uppercase text-gray-500">Alignment</span>
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
                value={alignment}
                onChange={(event) => setAlignment(event.target.value)}
                placeholder="Chaotic Good"
              />
            </label>
            <label className="block">
              <span className="text-xs font-semibold uppercase text-gray-500">Experience Points</span>
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
                type="number"
                value={experience}
                onChange={(event) => setExperience(Number(event.target.value))}
                min={0}
              />
            </label>
          </div>

          <label className="block">
            <span className="text-xs font-semibold uppercase text-gray-500">Notes</span>
            <textarea
              className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
              rows={3}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>

          {updateCharacter.isError ? (
            <p className="text-xs text-ember-red">Failed to update character. Please try again.</p>
          ) : null}
          {updateCharacter.isSuccess ? (
            <p className="text-xs text-forest-green">Character updated.</p>
          ) : null}

          <button
            className="w-full rounded bg-forest-green px-4 py-2 text-sm font-semibold text-white hover:bg-forest-green/90 disabled:opacity-50"
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
                className={`rounded border ${stateClass(score)} bg-parchment/60 p-3 text-center uppercase`}
              >
                <span className="text-xs font-semibold text-arcane-blue">{label}</span>
                <p className="text-xl font-bold">{score}</p>
                <p className="text-xs text-gray-600">{modifier >= 0 ? `+${modifier}` : modifier}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <h3 className="text-xs font-semibold uppercase text-gray-500">Alignment</h3>
              <p>{character.alignment ?? "Unaligned"}</p>
            </div>
            <div>
              <h3 className="text-xs font-semibold uppercase text-gray-500">Experience</h3>
              <p>{character.experience_points ?? 0} XP</p>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold uppercase text-gray-500">Background</h3>
            <p>{character.background ?? "Unknown origins"}</p>
          </div>

          {character.notes ? (
            <div>
              <h3 className="text-xs font-semibold uppercase text-gray-500">Notes</h3>
              <p>{character.notes}</p>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

function stateClass(score: number): string {
  if (score >= 16) return "border-forest-green";
  if (score <= 8) return "border-ember-red";
  return "border-gray-200";
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
