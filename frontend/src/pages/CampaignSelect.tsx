import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useCampaigns, useCreateCampaign } from "../hooks/useCampaigns";
import { useCharacters } from "../hooks/useCharacters";
import { useCreateDraft, useCharacterDrafts, useDeleteDraft } from "../hooks/useCharacterDrafts";

function CampaignSelect(): JSX.Element {
  const { data: campaigns = [], isLoading, isError } = useCampaigns();
  const {
    data: characters = [],
    isLoading: isLoadingCharacters,
    isError: isCharactersError
  } = useCharacters();
  const navigate = useNavigate();
  const createCampaign = useCreateCampaign();
  const { data: drafts = [], isLoading: isLoadingDrafts } = useCharacterDrafts();
  const createDraft = useCreateDraft();
  const deleteDraft = useDeleteDraft();
  const [isFormOpen, setFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const handleCreateCampaign = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim()) {
      setFormError("Campaign name is required.");
      return;
    }

    try {
      setFormError(null);
      await createCampaign.mutateAsync({ name, description: description || null });
      setName("");
      setDescription("");
      setFormOpen(false);
    } catch (error) {
      console.error("Failed to create campaign", error);
      setFormError("Unable to create campaign. Please try again.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-serif text-arcane-blue">Choose Your Adventure</h1>
        <p className="text-gray-700">
          Select an existing campaign or begin a fresh journey guided by the AI Dungeon Master.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="space-y-4 rounded-lg border border-arcane-blue/30 bg-white/80 p-4 shadow-sm">
          <header className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-arcane-blue">Your Campaigns</h2>
            <span className="text-xs uppercase text-gray-500">{campaigns.length} total</span>
          </header>
          {isLoading ? (
            <p className="text-sm text-gray-600">Summoning your ongoing tales...</p>
          ) : isError ? (
            <p className="text-sm text-ember-red">Unable to load campaigns. Try again shortly.</p>
          ) : campaigns.length === 0 ? (
            <p className="text-sm text-gray-600">
              No campaigns yet. Forge your party&apos;s path by creating a new character and adventure.
            </p>
          ) : (
            <ul className="space-y-3">
              {campaigns.map((campaign) => (
                <li
                  key={campaign.id}
                  className="rounded border border-arcane-blue/20 bg-parchment/60 p-3 transition hover:border-arcane-blue/60"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <h3 className="text-lg font-semibold text-arcane-blue">{campaign.name}</h3>
                      <p className="text-xs text-gray-600">
                        Updated {new Date(campaign.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Link
                        className="rounded bg-arcane-blue px-3 py-1 text-xs font-medium text-white hover:bg-arcane-blue/90"
                        to={`/game/${campaign.id}`}
                      >
                        Continue
                      </Link>
                      <Link
                        className="rounded border border-arcane-blue px-3 py-1 text-xs font-medium text-arcane-blue hover:bg-arcane-blue hover:text-white"
                        to={`/campaigns/${campaign.id}/manage`}
                      >
                        Manage
                      </Link>
                    </div>
                  </div>
                  <p className="mt-2 line-clamp-2 text-sm text-gray-700">
                    {campaign.description ?? "An untold story awaits."}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="space-y-4 rounded-lg border border-forest-green/30 bg-white/80 p-4 shadow-sm">
          <header className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-forest-green">Your Characters</h2>
            <span className="text-xs uppercase text-gray-500">{characters.length} total</span>
          </header>
          {isLoadingCharacters ? (
            <p className="text-sm text-gray-600">Gathering your legendary heroes...</p>
          ) : isCharactersError ? (
            <p className="text-sm text-ember-red">Unable to load character roster.</p>
          ) : characters.length === 0 ? (
            <p className="text-sm text-gray-600">
              No heroes on the roster yet. Create a character to embark on a new journey.
            </p>
          ) : (
            <ul className="space-y-3">
              {characters.map((character) => (
                <li
                  key={character.id}
                  className="rounded border border-forest-green/20 bg-parchment/60 p-3 transition hover:border-forest-green/60"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <h3 className="text-lg font-semibold text-forest-green">{character.name}</h3>
                      <p className="text-xs text-gray-600">
                        Level {character.level} {character.race ?? ""} {character.character_class ?? ""}
                      </p>
                    </div>
                    {character.campaign_id ? (
                      <Link
                        className="rounded border border-forest-green px-3 py-1 text-xs font-medium text-forest-green hover:bg-forest-green hover:text-white"
                        to={`/game/${character.campaign_id}`}
                      >
                        Join Campaign
                      </Link>
                    ) : null}
                  </div>
                  {character.background ? (
                    <p className="mt-2 line-clamp-2 text-sm text-gray-700">{character.background}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
          <div className="text-right">
            <Link
              className="inline-flex items-center rounded border border-forest-green px-3 py-1 text-xs font-medium text-forest-green hover:bg-forest-green hover:text-white"
              to="/characters/new"
            >
              Create Character
            </Link>
          </div>
        </article>
      </section>

      <div className="rounded-lg border border-arcane-blue/40 bg-white/80 p-4 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold text-arcane-blue">Forge a New Adventure</h2>
        <p className="text-sm text-gray-600">
          Start from scratch with the guided character builder, or create a fresh campaign realm for your solo journeys.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            className="inline-flex items-center rounded border border-forest-green px-4 py-2 text-sm font-medium text-forest-green hover:bg-forest-green hover:text-white"
            onClick={() => setFormOpen((prev) => !prev)}
            type="button"
          >
            {isFormOpen ? "Cancel Campaign" : "New Campaign"}
          </button>
          <button
            className="inline-flex items-center rounded border border-arcane-blue px-4 py-2 text-sm font-medium text-arcane-blue hover:bg-arcane-blue hover:text-white"
            onClick={async () => {
              const draft = await createDraft.mutateAsync({});
              navigate(`/builder?draft=${draft.id}`);
            }}
            type="button"
          >
            Launch Character Builder
          </button>
        </div>
        {isLoadingDrafts ? (
          <p className="mt-4 text-sm text-gray-600">Gathering your unfinished heroes...</p>
        ) : drafts.length > 0 ? (
          <div className="mt-4 space-y-2">
            <h3 className="text-sm font-semibold text-arcane-blue">In-progress Character Drafts</h3>
            <ul className="space-y-2">
              {drafts.map((draft) => (
                <li
                  key={draft.id}
                  className="flex items-center justify-between rounded border border-arcane-blue/20 bg-parchment/60 p-3 text-sm"
                >
                  <div>
                    <p className="font-medium text-arcane-blue">{draft.name ?? "Unnamed Hero"}</p>
                    <p className="text-xs text-gray-600">
                      Step: {draft.current_step ?? "intro"} • Level {draft.starting_level}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="rounded border border-arcane-blue px-3 py-1 text-xs text-arcane-blue hover:bg-arcane-blue hover:text-white"
                      onClick={() => navigate(`/builder?draft=${draft.id}`)}
                      type="button"
                    >
                      Resume
                    </button>
                    <button
                      className="rounded border border-ember-red px-3 py-1 text-xs text-ember-red hover:bg-ember-red hover:text-white"
                      onClick={() => deleteDraft.mutate(draft.id)}
                      type="button"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      {isFormOpen ? (
        <form
          className="space-y-4 rounded-lg border border-arcane-blue/40 bg-white/80 p-6 shadow"
          onSubmit={handleCreateCampaign}
        >
          <div>
            <label className="block text-sm font-semibold text-arcane-blue">
              Campaign Name
              <input
                className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
                placeholder="Shadows of the Moonsea"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-semibold text-arcane-blue">
              Premise (optional)
              <textarea
                className="mt-1 w-full rounded border border-gray-300 p-2 focus:border-arcane-blue focus:outline-none"
                placeholder="A tale of intrigue and eldritch forces..."
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                rows={3}
              />
            </label>
          </div>

          {formError ? <p className="text-sm text-ember-red">{formError}</p> : null}

          <button
            className="w-full rounded bg-forest-green px-4 py-2 text-sm font-semibold text-white hover:bg-forest-green/90 disabled:opacity-50"
            disabled={createCampaign.isPending}
            type="submit"
          >
            {createCampaign.isPending ? "Forging realm..." : "Create Campaign"}
          </button>
        </form>
      ) : null}
    </div>
  );
}

export default CampaignSelect;
