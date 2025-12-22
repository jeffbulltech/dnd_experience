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
  const {
    data: characters = [],
    isLoading: isLoadingCharacters,
    isError: isCharactersError
  } = useCharacters({ campaignId: numericCampaignId });
  const activeCharacter = useMemo(() => characters[0], [characters]);

  const { data: inventoryItems = [], isLoading: isLoadingInventory } = useInventory({
    characterId: activeCharacter?.id
  });
  const { deleteItem } = useInventoryMutations(activeCharacter?.id);
  const {
    data: combatState,
    isLoading: isLoadingCombatState
  } = useCombatState(numericCampaignId);
  const { addParticipant, updateParticipant, deleteParticipant } = useCombatMutations(numericCampaignId);

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
        <DiceRoller campaignId={numericCampaignId} characterId={activeCharacter?.id} />
        <InventoryPanel
          items={inventoryItems}
          isLoading={isLoadingInventory}
          onRemove={(itemId) => deleteItem.mutate(itemId)}
        />
        {isLoadingCharacters ? (
          <div className="parchment-card p-4">
            <p className="text-sm font-display text-gray-700">Fetching hero details...</p>
          </div>
        ) : isCharactersError ? (
          <div className="parchment-card p-4">
            <p className="text-sm font-medium text-ember-red-800">Could not load character information.</p>
          </div>
        ) : activeCharacter ? (
          <CharacterSheet character={activeCharacter} />
        ) : (
          <div className="parchment-card p-4 text-center">
            <p className="text-sm font-display text-gray-700">
              No character is linked to this campaign yet. Create one to begin your journey.
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
      </aside>
    </div>
  );
}

export default Game;
