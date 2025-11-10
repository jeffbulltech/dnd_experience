import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useCampaigns } from "../hooks/useCampaigns";
import { useCreateCharacter } from "../hooks/useCharacters";

const classes = ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger"];
const races = ["Human", "Elf", "Dwarf", "Halfling", "Tiefling"];

function CharacterCreation(): JSX.Element {
  const navigate = useNavigate();
  const { data: campaigns = [], isLoading: isLoadingCampaigns } = useCampaigns();
  const createCharacter = useCreateCharacter();

  const [name, setName] = useState("");
  const [selectedClass, setSelectedClass] = useState(classes[0]);
  const [selectedRace, setSelectedRace] = useState(races[0]);
  const [background, setBackground] = useState("");
  const [campaignId, setCampaignId] = useState<number | undefined>(undefined);

  useEffect(() => {
    if (!campaignId && campaigns.length > 0) {
      setCampaignId(campaigns[0].id);
    }
  }, [campaignId, campaigns]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await createCharacter.mutateAsync({
      name,
      character_class: selectedClass,
      race: selectedRace,
      background: background || undefined,
      level: 1,
      campaign_id: campaignId
    });
    navigate("/campaigns");
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-serif text-arcane-blue">Forge a Hero</h1>
        <p className="text-gray-700">Follow the guided steps to breathe life into your next adventurer.</p>
      </header>

      <form className="space-y-4 rounded-lg border border-arcane-blue/40 bg-white/80 p-6 shadow" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-semibold text-arcane-blue">Name</span>
          <input
            className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
            placeholder="Elaria Stormsinger"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-arcane-blue">Class</span>
          <select
            className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
            value={selectedClass}
            onChange={(event) => setSelectedClass(event.target.value)}
          >
            {classes.map((entry) => (
              <option key={entry}>{entry}</option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-arcane-blue">Race</span>
          <select
            className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
            value={selectedRace}
            onChange={(event) => setSelectedRace(event.target.value)}
          >
            {races.map((entry) => (
              <option key={entry}>{entry}</option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-arcane-blue">Background</span>
          <textarea
            className="mt-1 w-full resize-none rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
            placeholder="Scholar from the Ivory Archives..."
            value={background}
            onChange={(event) => setBackground(event.target.value)}
            rows={3}
          />
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-arcane-blue">Assign to Campaign</span>
          <select
            className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
            value={campaignId ?? ""}
            onChange={(event) => setCampaignId(event.target.value ? Number(event.target.value) : undefined)}
            disabled={isLoadingCampaigns || campaigns.length === 0}
          >
            {campaigns.length === 0 ? <option value="">No campaigns available</option> : null}
            {campaigns.map((campaign) => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
        </label>

        <button
          className="w-full rounded bg-forest-green px-4 py-2 text-sm font-semibold text-white hover:bg-forest-green/90"
          disabled={createCharacter.isPending}
          type="submit"
        >
          {createCharacter.isPending ? "Forging..." : "Begin Adventure"}
        </button>
      </form>
    </div>
  );
}

export default CharacterCreation;
