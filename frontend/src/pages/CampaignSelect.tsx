import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAdventures } from "../hooks/useAdventures";
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
  const { data: adventures = [], isLoading: isLoadingAdventures } = useAdventures();
  const [isFormOpen, setFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [adventureTemplateId, setAdventureTemplateId] = useState<string>("custom");
  const [formError, setFormError] = useState<string | null>(null);

  const handleCreateCampaign = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim()) {
      setFormError("Campaign name is required.");
      return;
    }

    try {
      setFormError(null);
      await createCampaign.mutateAsync({
        name,
        description: description || null,
        adventure_template_id: adventureTemplateId === "custom" ? null : adventureTemplateId,
      });
      setName("");
      setDescription("");
      setAdventureTemplateId("custom");
      setFormOpen(false);
      // Scroll to top to show the new campaign
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error("Failed to create campaign", error);
      setFormError("Unable to create campaign. Please try again.");
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-10 p-8">
      <header className="space-y-4 text-center">
        <div className="mb-6 text-7xl font-display">⚔️</div>
        <h1 className="text-5xl font-display font-bold text-dragon-gold-300 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
          Choose Your Adventure
        </h1>
        <p className="text-xl font-display text-parchment-200/90">
          Select an existing campaign or begin a fresh journey guided by the AI Dungeon Master.
        </p>
      </header>

      <section className="grid gap-8 lg:grid-cols-2">
        <article className="parchment-card space-y-5 p-6">
          <header className="flex items-center justify-between border-b-2 border-arcane-blue-800/30 pb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📜</span>
              <h2 className="text-2xl font-display font-bold text-arcane-blue-900">Your Campaigns</h2>
            </div>
            <span className="rounded-md bg-arcane-blue-100 px-3 py-1.5 text-sm font-display font-semibold uppercase text-arcane-blue-800">
              {campaigns.length} total
            </span>
          </header>
          {isLoading ? (
            <div className="flex items-center gap-3 text-lg text-gray-700">
              <span className="text-xl">🔮</span>
              <p>Summoning your ongoing tales...</p>
            </div>
          ) : isError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-4">
              <p className="text-lg font-medium text-ember-red-800">Unable to load campaigns. Try again shortly.</p>
            </div>
          ) : campaigns.length === 0 ? (
            <p className="text-lg text-gray-700 leading-relaxed">
              No campaigns yet. Forge your party&apos;s path by creating a new character and adventure.
            </p>
          ) : (
            <ul className="space-y-4">
              {campaigns.map((campaign) => (
                <li
                  key={campaign.id}
                  className="rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-5 transition-all hover:border-arcane-blue-400/60 hover:shadow-md"
                >
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <div>
                      <h3 className="text-xl font-display font-bold text-arcane-blue-900">{campaign.name}</h3>
                      <p className="text-sm font-medium text-gray-600">
                        Updated {new Date(campaign.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <Link
                        className="fantasy-button text-sm px-4 py-2"
                        to={`/game/${campaign.id}`}
                      >
                        Continue
                      </Link>
                    </div>
                  </div>
                  <p className="line-clamp-2 text-lg text-gray-700 leading-relaxed">
                    {campaign.description ?? "An untold story awaits."}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="parchment-card space-y-5 p-6">
          <header className="flex items-center justify-between border-b-2 border-forest-green-800/30 pb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🛡</span>
              <h2 className="text-2xl font-display font-bold text-forest-green-900">Your Characters</h2>
            </div>
            <span className="rounded-md bg-forest-green-100 px-3 py-1.5 text-sm font-display font-semibold uppercase text-forest-green-800">
              {characters.length} total
            </span>
          </header>
          {isLoadingCharacters ? (
            <div className="flex items-center gap-3 text-lg text-gray-700">
              <span className="text-xl">🔮</span>
              <p>Gathering your legendary heroes...</p>
            </div>
          ) : isCharactersError ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-4">
              <p className="text-lg font-medium text-ember-red-800">Unable to load character roster.</p>
            </div>
          ) : characters.length === 0 ? (
            <p className="text-lg text-gray-700 leading-relaxed">
              No heroes on the roster yet. Create a character to embark on a new journey.
            </p>
          ) : (
            <ul className="space-y-4">
              {characters.map((character) => (
                <li
                  key={character.id}
                  className="rounded-md border-2 border-forest-green-200/50 bg-parchment-50/90 p-5 transition-all hover:border-forest-green-400/60 hover:shadow-md"
                >
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <div>
                      <h3 className="text-xl font-display font-bold text-forest-green-900">{character.name}</h3>
                      <p className="text-sm font-medium text-gray-600">
                        Level {character.level} {character.race ?? ""} {character.character_class ?? ""}
                      </p>
                    </div>
                    {character.campaign_id ? (
                      <Link
                        className="fantasy-button text-sm px-4 py-2 bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
                        to={`/game/${character.campaign_id}`}
                      >
                        Join Campaign
                      </Link>
                    ) : null}
                  </div>
                  {character.background ? (
                    <p className="line-clamp-2 text-lg text-gray-700 leading-relaxed">{character.background}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
          <div className="text-right pt-3">
            <Link
              className="fantasy-button inline-flex items-center text-sm px-5 py-2.5 bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
              to="/characters/new"
            >
              Create Character
            </Link>
          </div>
        </article>
      </section>

      <div className="parchment-card p-8">
        <div className="mb-5 flex items-center gap-3">
          <span className="text-4xl">⚔️</span>
          <h2 className="text-3xl font-display font-bold text-arcane-blue-900">Forge a New Adventure</h2>
        </div>
        <p className="mb-6 text-lg text-gray-700 leading-relaxed">
          Start from scratch with the guided character builder, or create a fresh campaign realm for your solo journeys.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            className="fantasy-button bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800"
            onClick={() => setFormOpen(true)}
            type="button"
          >
            New Campaign
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
          <div className="mt-5 flex items-center gap-3 text-lg text-gray-700">
            <span className="text-xl">🔮</span>
            <p>Gathering your unfinished heroes...</p>
          </div>
        ) : drafts.length > 0 ? (
          <div className="mt-8 space-y-4 border-t-2 border-arcane-blue-800/30 pt-6">
            <h3 className="text-lg font-display font-bold text-arcane-blue-900">In-progress Character Drafts</h3>
            <ul className="space-y-3">
              {drafts.map((draft) => (
                <li
                  key={draft.id}
                  className="flex items-center justify-between rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-4 text-base"
                >
                  <div>
                    <p className="font-display font-bold text-arcane-blue-900">{draft.name ?? "Unnamed Hero"}</p>
                    <p className="text-sm font-medium text-gray-600">
                      Step: {draft.current_step ?? "intro"} • Level {draft.starting_level}
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      className="fantasy-button text-sm px-4 py-2"
                      onClick={() => navigate(`/builder?draft=${draft.id}`)}
                      type="button"
                    >
                      Resume
                    </button>
                    <button
                      className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 px-4 py-2 text-sm font-display font-semibold text-ember-red-800 transition-colors hover:bg-ember-red-100"
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
        <>
          {/* Modal Overlay */}
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
            onClick={() => setFormOpen(false)}
          >
            {/* Modal Content */}
            <div
              className="parchment-card w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-6 p-8"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-3xl font-display font-bold text-arcane-blue-900">Create New Campaign</h2>
                <button
                  className="text-2xl text-gray-600 hover:text-gray-900 transition-colors"
                  onClick={() => {
                    setFormOpen(false);
                    setFormError(null);
                  }}
                  type="button"
                  aria-label="Close"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleCreateCampaign} className="space-y-6">
                <div>
                  <label className="block text-base font-display font-semibold text-arcane-blue-900">
                    Campaign Name
                    <input
                      className="fantasy-input mt-3 w-full"
                      placeholder="Shadows of the Moonsea"
                      value={name}
                      onChange={(event) => setName(event.target.value)}
                      required
                    />
                  </label>
                </div>

                <div>
                  <label className="block text-base font-display font-semibold text-arcane-blue-900 mb-3">
                    Adventure Selection
                  </label>
                  {isLoadingAdventures ? (
                    <p className="text-lg text-gray-700">Loading adventures...</p>
                  ) : (
                    <div className="space-y-3 max-h-64 overflow-y-auto scroll-container">
                      <label className="flex items-start gap-3 p-4 rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 cursor-pointer hover:border-arcane-blue-400/60 transition-colors">
                        <input
                          type="radio"
                          name="adventure"
                          value="custom"
                          checked={adventureTemplateId === "custom"}
                          onChange={(e) => setAdventureTemplateId(e.target.value)}
                          className="mt-1"
                        />
                        <div className="flex-1">
                          <div className="font-display font-bold text-lg text-arcane-blue-900">Create Custom Adventure</div>
                          <p className="text-base text-gray-700 mt-1">
                            Let the AI Game Master create a unique adventure tailored to your campaign.
                          </p>
                        </div>
                      </label>

                      {adventures.map((adventure) => (
                        <label
                          key={adventure.id}
                          className="flex items-start gap-3 p-4 rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 cursor-pointer hover:border-arcane-blue-400/60 transition-colors"
                        >
                          <input
                            type="radio"
                            name="adventure"
                            value={adventure.id}
                            checked={adventureTemplateId === adventure.id}
                            onChange={(e) => setAdventureTemplateId(e.target.value)}
                            className="mt-1"
                          />
                          <div className="flex-1">
                            <div className="font-display font-bold text-lg text-arcane-blue-900">{adventure.name}</div>
                            <p className="text-sm text-gray-600 mt-1">
                              {adventure.setting} • Levels {adventure.level_range}
                            </p>
                            <p className="text-base text-gray-700 mt-2">{adventure.description}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-base font-display font-semibold text-arcane-blue-900">
                    Premise (optional)
                    <textarea
                      className="fantasy-input mt-3 w-full"
                      placeholder="A tale of intrigue and eldritch forces..."
                      value={description}
                      onChange={(event) => setDescription(event.target.value)}
                      rows={4}
                    />
                  </label>
                </div>

                {formError ? (
                  <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-4">
                    <p className="text-base font-medium text-ember-red-800">{formError}</p>
                  </div>
                ) : null}

                <div className="flex gap-3">
                  <button
                    className="fantasy-button flex-1 bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800 disabled:opacity-50"
                    disabled={createCampaign.isPending}
                    type="submit"
                  >
                    {createCampaign.isPending ? "Forging realm..." : "Create Campaign"}
                  </button>
                  <button
                    className="fantasy-button bg-gradient-to-b from-ember-red-700 to-ember-red-900 hover:from-ember-red-600 hover:to-ember-red-800"
                    onClick={() => {
                      setFormOpen(false);
                      setFormError(null);
                    }}
                    type="button"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}

export default CampaignSelect;
