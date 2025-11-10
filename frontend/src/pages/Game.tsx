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
    <div className="grid min-h-screen grid-cols-1 gap-4 bg-parchment/80 p-4 lg:grid-cols-[2fr,1fr]">
      <section className="space-y-4">
        <div className="rounded-lg border border-arcane-blue/40 bg-white/80 p-4 shadow">
          {isLoadingState ? (
            <p className="text-sm text-gray-600">Consulting the chronicles...</p>
          ) : isGameStateError ? (
            <p className="text-sm text-ember-red">Unable to retrieve the current adventure state.</p>
          ) : gameState ? (
            <div className="space-y-2">
              <h1 className="text-2xl font-serif text-arcane-blue">Adventure Overview</h1>
              <p className="text-sm text-gray-700">
                <strong>Location:</strong> {gameState.location ?? "Unknown wilds"}
              </p>
              {gameState.summary ? <p className="text-sm text-gray-700">{gameState.summary}</p> : null}
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
          <p className="text-sm text-gray-600">Fetching hero details...</p>
        ) : isCharactersError ? (
          <p className="text-sm text-ember-red">Could not load character information.</p>
        ) : activeCharacter ? (
          <CharacterSheet character={activeCharacter} />
        ) : (
          <p className="rounded border border-dashed border-arcane-blue/40 bg-white/70 p-3 text-sm text-gray-600">
            No character is linked to this campaign yet. Create one to begin your journey.
          </p>
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
