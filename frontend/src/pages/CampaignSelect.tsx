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
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <header className="space-y-3 text-center">
        <div className="mb-4 text-6xl font-display">⚔️</div>
        <h1 className="text-4xl font-display font-bold text-dragon-gold-300 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
          Choose Your Adventure
        </h1>
        <p className="text-lg font-display text-parchment-200/90">
          Select an existing campaign or begin a fresh journey guided by the AI Dungeon Master.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="parchment-card space-y-4 p-5">
          <header className="flex items-center justify-between border-b-2 border-arcane-blue-800/30 pb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📜</span>
              <h2 className="text-xl font-display font-bold text-arcane-blue-900">Your Campaigns</h2>
            </div>
            <span className="rounded-md bg-arcane-blue-100 px-2 py-1 text-xs font-display font-semibold uppercase text-arcane-blue-800">
              {campaigns.length} total
            </span>
          </header>
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>🔮</span>
              <p className="font-display">Summoning your ongoing tales...</p>
            </div>
          ) : isError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-3">
              <p className="text-sm font-medium text-ember-red-800">Unable to load campaigns. Try again shortly.</p>
            </div>
          ) : campaigns.length === 0 ? (
            <p className="text-sm font-display text-gray-700">
              No campaigns yet. Forge your party&apos;s path by creating a new character and adventure.
            </p>
          ) : (
            <ul className="space-y-3">
              {campaigns.map((campaign) => (
                <li
                  key={campaign.id}
                  className="rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-4 transition-all hover:border-arcane-blue-400/60 hover:shadow-md"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div>
                      <h3 className="text-lg font-display font-bold text-arcane-blue-900">{campaign.name}</h3>
                      <p className="text-xs font-medium text-gray-600">
                        Updated {new Date(campaign.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Link
                        className="fantasy-button text-xs px-3 py-1"
                        to={`/game/${campaign.id}`}
                      >
                        Continue
                      </Link>
                      <Link
                        className="rounded-md border-2 border-arcane-blue-600 bg-arcane-blue-50 px-3 py-1 text-xs font-display font-semibold text-arcane-blue-800 transition-colors hover:bg-arcane-blue-200"
                        to={`/campaigns/${campaign.id}/manage`}
                      >
                        Manage
                      </Link>
                    </div>
                  </div>
                  <p className="line-clamp-2 text-sm text-gray-700">
                    {campaign.description ?? "An untold story awaits."}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="parchment-card space-y-4 p-5">
          <header className="flex items-center justify-between border-b-2 border-forest-green-800/30 pb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🛡</span>
              <h2 className="text-xl font-display font-bold text-forest-green-900">Your Characters</h2>
            </div>
            <span className="rounded-md bg-forest-green-100 px-2 py-1 text-xs font-display font-semibold uppercase text-forest-green-800">
              {characters.length} total
            </span>
          </header>
          {isLoadingCharacters ? (
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <span>🔮</span>
              <p className="font-display">Gathering your legendary heroes...</p>
            </div>
          ) : isCharactersError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-3">
              <p className="text-sm font-medium text-ember-red-800">Unable to load character roster.</p>
            </div>
          ) : characters.length === 0 ? (
            <p className="text-sm font-display text-gray-700">
              No heroes on the roster yet. Create a character to embark on a new journey.
            </p>
          ) : (
            <ul className="space-y-3">
              {characters.map((character) => (
                <li
                  key={character.id}
                  className="rounded-md border-2 border-forest-green-200/50 bg-parchment-50/90 p-4 transition-all hover:border-forest-green-400/60 hover:shadow-md"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div>
                      <h3 className="text-lg font-display font-bold text-forest-green-900">{character.name}</h3>
                      <p className="text-xs font-medium text-gray-600">
                        Level {character.level} {character.race ?? ""} {character.character_class ?? ""}
                      </p>
                    </div>
                    {character.campaign_id ? (
                      <Link
                        className="fantasy-button text-xs px-3 py-1 bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
                        to={`/game/${character.campaign_id}`}
                      >
                        Join Campaign
                      </Link>
                    ) : null}
                  </div>
                  {character.background ? (
                    <p className="line-clamp-2 text-sm text-gray-700">{character.background}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
          <div className="text-right pt-2">
            <Link
              className="fantasy-button inline-flex items-center text-xs px-4 py-2 bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
              to="/characters/new"
            >
              Create Character
            </Link>
          </div>
        </article>
      </section>

      <div className="parchment-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <span className="text-3xl">⚔️</span>
          <h2 className="text-2xl font-display font-bold text-arcane-blue-900">Forge a New Adventure</h2>
        </div>
        <p className="mb-5 text-sm font-display text-gray-700">
          Start from scratch with the guided character builder, or create a fresh campaign realm for your solo journeys.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            className="fantasy-button bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
            onClick={() => setFormOpen((prev) => !prev)}
            type="button"
          >
            {isFormOpen ? "Cancel Campaign" : "New Campaign"}
          </button>
          <button
            className="fantasy-button"
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
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-700">
            <span>🔮</span>
            <p className="font-display">Gathering your unfinished heroes...</p>
          </div>
        ) : drafts.length > 0 ? (
          <div className="mt-6 space-y-3 border-t-2 border-arcane-blue-800/30 pt-4">
            <h3 className="text-sm font-display font-bold text-arcane-blue-900">In-progress Character Drafts</h3>
            <ul className="space-y-2">
              {drafts.map((draft) => (
                <li
                  key={draft.id}
                  className="flex items-center justify-between rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-3 text-sm"
                >
                  <div>
                    <p className="font-display font-bold text-arcane-blue-900">{draft.name ?? "Unnamed Hero"}</p>
                    <p className="text-xs font-medium text-gray-600">
                      Step: {draft.current_step ?? "intro"} • Level {draft.starting_level}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="fantasy-button text-xs px-3 py-1"
                      onClick={() => navigate(`/builder?draft=${draft.id}`)}
                      type="button"
                    >
                      Resume
                    </button>
                    <button
                      className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 px-3 py-1 text-xs font-display font-semibold text-ember-red-800 transition-colors hover:bg-ember-red-100"
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
          className="parchment-card space-y-5 p-6"
          onSubmit={handleCreateCampaign}
        >
          <div>
            <label className="block text-sm font-display font-semibold text-arcane-blue-900">
              Campaign Name
              <input
                className="fantasy-input mt-2 w-full"
                placeholder="Shadows of the Moonsea"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-display font-semibold text-arcane-blue-900">
              Premise (optional)
              <textarea
                className="fantasy-input mt-2 w-full"
                placeholder="A tale of intrigue and eldritch forces..."
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                rows={3}
              />
            </label>
          </div>

          {formError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-3">
              <p className="text-sm font-medium text-ember-red-800">{formError}</p>
            </div>
          ) : null}

          <button
            className="fantasy-button w-full bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800 disabled:opacity-50"
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
