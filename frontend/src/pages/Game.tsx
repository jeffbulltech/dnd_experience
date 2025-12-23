import { useEffect, useMemo, useState } from "react";
import { Navigate, useParams } from "react-router-dom";

import ChatInterface from "../components/ChatInterface/ChatInterface";
import CharacterSheet from "../components/CharacterSheet/CharacterSheet";
import CombatTracker from "../components/CombatTracker/CombatTracker";
import DiceRoller from "../components/DiceRoller/DiceRoller";
import InventoryPanel from "../components/Inventory/InventoryPanel";
import QuestLog from "../components/QuestLog/QuestLog";
import GameStateEditor from "../components/GameStateEditor/GameStateEditor";
import { useCharacters } from "../hooks/useCharacters";
import { useGameState } from "../hooks/useGameState";
import { useCombatState } from "../hooks/useCombat";
import { useCombatMutations } from "../hooks/useCombatMutations";
import { useInventory, useInventoryMutations } from "../hooks/useInventory";
import { useChatHistory } from "../hooks/useChatHistory";
import { useUpdateCharacter } from "../hooks/useCharacters";

function Game(): JSX.Element {
  const { campaignId } = useParams();
  const numericCampaignId = campaignId ? Number(campaignId) : undefined;
  const [isCombatActive, setCombatActive] = useState(false);

  useEffect(() => {
    setCombatActive(false);
  }, [numericCampaignId]);

  const {
    data: gameState,
    isLoading: isLoadingState,
    isError: isGameStateError
  } = useGameState(numericCampaignId);
  const { data: chatHistory } = useChatHistory(numericCampaignId);
  
  // Check if story has started (has any player messages beyond welcome)
  const storyHasStarted = useMemo(() => {
    if (!chatHistory) return false;
    // Story has started if there are any player messages
    return chatHistory.some((entry) => entry.role === "player");
  }, [chatHistory]);

  // Always fetch campaign characters to see if one is linked
  const {
    data: campaignCharacters = [],
    isLoading: isLoadingCampaignCharacters,
    isError: isCampaignCharactersError
  } = useCharacters({ campaignId: numericCampaignId });
  
  // Fetch all user characters when no character is linked (for selection)
  const {
    data: allUserCharacters = [],
    isLoading: isLoadingAllCharacters
  } = useCharacters({ campaignId: undefined });

  const activeCharacter = useMemo(() => campaignCharacters[0], [campaignCharacters]);
  const updateCharacter = useUpdateCharacter();
  
  // Get available characters for selection (characters not linked to any campaign)
  // Show selection if no character is linked, regardless of whether story has started
  const availableCharacters = useMemo(() => {
    if (activeCharacter) return []; // Don't show if character is already linked
    // Only show characters that aren't linked to any campaign yet
    return allUserCharacters.filter((char) => !char.campaign_id);
  }, [allUserCharacters, activeCharacter]);

  const { data: inventoryItems = [], isLoading: isLoadingInventory } = useInventory({
    characterId: activeCharacter?.id
  });
  const { deleteItem } = useInventoryMutations(activeCharacter?.id);
  const {
    data: combatState,
    isLoading: isLoadingCombatState
  } = useCombatState(numericCampaignId);
  const { addParticipant, updateParticipant, deleteParticipant } = useCombatMutations(numericCampaignId);

  const handleSelectCharacter = async (characterId: number) => {
    try {
      await updateCharacter.mutateAsync({
        id: characterId,
        updates: { campaign_id: numericCampaignId }
      });
    } catch (error) {
      console.error("Failed to link character to campaign", error);
    }
  };

  useEffect(() => {
    if (combatState && Object.keys(combatState.combatants).length > 0) {
      setCombatActive(true);
    } else {
      setCombatActive(false);
    }
  }, [combatState]);

  if (!numericCampaignId) {
    return <Navigate to="/campaigns" replace />;
  }

  return (
    <div className="grid min-h-screen grid-cols-1 gap-6 bg-gradient-to-br from-shadow-black via-arcane-blue-900/20 to-shadow-black p-6 lg:grid-cols-[2fr,1fr]">
      <section className="space-y-6">
        <div className="parchment-card p-6">
          {isLoadingState ? (
            <div className="flex items-center gap-3">
              <span className="text-2xl">📜</span>
              <p className="text-sm font-display text-gray-700">Consulting the chronicles...</p>
            </div>
          ) : isGameStateError ? (
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              <p className="text-sm font-medium text-ember-red-800">Unable to retrieve the current adventure state.</p>
            </div>
          ) : gameState ? (
            <div className="space-y-3">
              <h1 className="text-3xl font-display font-bold text-arcane-blue-900">Adventure Overview</h1>
              
              {/* Character Selection - Show if no character is linked */}
              {!activeCharacter && availableCharacters.length > 0 && (
                <div className="mt-4 rounded-md border-2 border-dragon-gold-400/60 bg-dragon-gold-50/90 p-4">
                  <h2 className="text-xl font-display font-bold text-arcane-blue-900 mb-3">
                    Choose Your Hero
                  </h2>
                  <p className="text-base text-gray-700 mb-4">
                    {storyHasStarted 
                      ? "You need to select a character to continue this adventure. Your character will be linked to this campaign."
                      : "Select a character to begin this adventure. Once you start, you'll be committed to this hero for the campaign."}
                  </p>
                  <div className="space-y-2 max-h-64 overflow-y-auto scroll-container">
                    {isLoadingAllCharacters ? (
                      <p className="text-sm text-gray-600">Loading characters...</p>
                    ) : (
                      availableCharacters.map((character) => (
                        <button
                          key={character.id}
                          onClick={() => handleSelectCharacter(character.id)}
                          disabled={updateCharacter.isPending}
                          className="w-full text-left p-3 rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 hover:border-arcane-blue-400/60 transition-colors disabled:opacity-50"
                        >
                          <div className="font-display font-bold text-lg text-arcane-blue-900">
                            {character.name}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {character.character_class && character.race ? (
                              <>
                                Level {character.level} {character.race} {character.character_class}
                              </>
                            ) : (
                              `Level ${character.level}`
                            )}
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                  {updateCharacter.isPending && (
                    <p className="text-sm text-gray-600 mt-2">Linking character...</p>
                  )}
                </div>
              )}

              {/* Show message if no characters available */}
              {!activeCharacter && availableCharacters.length === 0 && !isLoadingAllCharacters && (
                <div className="mt-4 rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-4">
                  <p className="text-base text-gray-700">
                    You don't have any available characters yet. Create one using the Character Builder to begin this adventure.
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-800">
                  <span className="font-display text-arcane-blue-800">📍 Location:</span>{" "}
                  <span className="text-gray-700">{gameState.location ?? "Unknown wilds"}</span>
                </p>
                {gameState.summary ? (
                  <div className="mt-3 rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-3">
                    <p className="text-sm leading-relaxed text-gray-700">{gameState.summary}</p>
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
        </div>

        {numericCampaignId ? <GameStateEditor campaignId={numericCampaignId} gameState={gameState} /> : null}

        <ChatInterface campaignId={numericCampaignId} characterId={activeCharacter?.id} onToggleCombat={setCombatActive} />

        <QuestLog quests={gameState?.active_quests} />
      </section>
      <aside className="space-y-4">
        <InventoryPanel
          items={inventoryItems}
          isLoading={isLoadingInventory}
          onRemove={(itemId) => deleteItem.mutate(itemId)}
        />
        {isLoadingCampaignCharacters ? (
          <div className="parchment-card p-4">
            <p className="text-sm font-display text-gray-700">Fetching hero details...</p>
          </div>
        ) : isCampaignCharactersError ? (
          <div className="parchment-card p-4">
            <p className="text-sm font-medium text-ember-red-800">Could not load character information.</p>
          </div>
        ) : activeCharacter ? (
          <CharacterSheet character={activeCharacter} />
        ) : (
          <div className="parchment-card p-4 text-center">
            <p className="text-sm font-display text-gray-700">
              {storyHasStarted 
                ? "No character is linked to this campaign yet. Create one to begin your journey."
                : "Select a character from the Adventure Overview to begin your journey."}
            </p>
          </div>
        )}
        <CombatTracker
          state={combatState}
          isLoading={isLoadingCombatState}
          onAddParticipant={(payload) =>
            addParticipant.mutate({
              ...payload
            })
          }
          onUpdateParticipant={(participantId, updates) =>
            updateParticipant.mutate({ participantId, updates })
          }
          onRemoveParticipant={(participantId) => deleteParticipant.mutate(participantId)}
          disabled={addParticipant.isPending || updateParticipant.isPending || deleteParticipant.isPending}
        />
        <DiceRoller campaignId={numericCampaignId} characterId={activeCharacter?.id} />
      </aside>
    </div>
  );
}

export default Game;
