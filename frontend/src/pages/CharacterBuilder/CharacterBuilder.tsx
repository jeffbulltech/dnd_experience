import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { AxiosError } from "axios";

import AbilityScoreStep from "./AbilityScoreStep";
import OriginStep from "./OriginStep";
import ClassStep from "./ClassStep";
import ProficiencyStep from "./ProficiencyStep";
import EquipmentStep from "./EquipmentStep";
import SpellStep from "./SpellStep";
import {
  useCharacterDraft,
  useCreateDraft,
  useUpdateDraftStep,
  AbilityScoreStepPayload,
  OriginStepPayload,
  ClassStepPayload,
  ProficiencyStepPayload,
  EquipmentStepPayload,
  SpellStepPayload
} from "../../hooks/useCharacterDrafts";
import { useCatalog } from "../../hooks/useCatalog";

const STEP_ORDER = ["ability_scores", "origin", "class", "proficiencies", "equipment", "spells"] as const;
type BuilderStep = (typeof STEP_ORDER)[number];

type StepPayloadMap = {
  ability_scores: AbilityScoreStepPayload;
  origin: OriginStepPayload;
  class: ClassStepPayload;
  proficiencies: ProficiencyStepPayload;
  equipment: EquipmentStepPayload;
  spells: SpellStepPayload;
};

type StepPayloadFor<S extends BuilderStep> = StepPayloadMap[S];

function CharacterBuilder(): JSX.Element {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const draftIdParam = searchParams.get("draft");
  const draftId = draftIdParam ? Number(draftIdParam) : undefined;

  const { data: catalog, isLoading: isCatalogLoading } = useCatalog();
  const { data: activeDraft, isLoading: isLoadingDraft } = useCharacterDraft(draftId);
  const createDraft = useCreateDraft();
  const updateStep = useUpdateDraftStep<BuilderStep>();

  const [stepIndex, setStepIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentStep: BuilderStep = STEP_ORDER[stepIndex];

  const handleStepUpdate = <S extends BuilderStep>(step: S, payload: StepPayloadFor<S>) => {
    if (!activeDraft || !draftId) return;
    updateStep.mutate(
      { draftId, step, data: payload },
      {
        onError: (error) => {
          const message = (error as AxiosError<{ detail?: string }>)?.response?.data?.detail;
          setErrorMessage(message ?? "Unable to save changes. Please review your entries.");
        },
        onSuccess: () => setErrorMessage(null)
      }
    );
  };

  const handleContinue = async () => {
    if (!draftId) {
      const draft = await createDraft.mutateAsync({});
      setSearchParams({ draft: String(draft.id) }, { replace: true });
      return;
    }
    if (stepIndex < STEP_ORDER.length - 1) {
      setStepIndex((prev) => prev + 1);
    } else {
      navigate("/campaigns", { replace: true });
    }
  };

  const abilityStepData = activeDraft?.step_data?.ability_scores as AbilityScoreStepPayload | undefined;
  const originStepData = activeDraft?.step_data?.origin as OriginStepPayload | undefined;
  const classStepData = activeDraft?.step_data?.class as ClassStepPayload | undefined;
  const profStepData = activeDraft?.step_data?.proficiencies as ProficiencyStepPayload | undefined;
  const equipmentStepData = activeDraft?.step_data?.equipment as EquipmentStepPayload | undefined;
  const spellStepData = activeDraft?.step_data?.spells as SpellStepPayload | undefined;

  const disableStepInteraction = !activeDraft || updateStep.isPending;

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <header className="space-y-3">
        <div className="flex items-center justify-between">
          <button
            className="flex items-center gap-2 text-sm font-semibold text-arcane-blue hover:text-arcane-blue/80"
            onClick={() => navigate("/campaigns")}
            type="button"
          >
            <span aria-hidden="true">←</span>
            Back to Campaigns
          </button>
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-serif text-arcane-blue">Character Builder</h1>
          <p className="text-gray-700">
            Guided creation inspired by the official Dungeons & Dragons 5E ruleset. Progress is saved automatically.
          </p>
        </div>
      </header>

      <nav className="flex gap-2">
        {STEP_ORDER.map((step, index) => (
          <button
            key={step}
            className={`rounded px-3 py-1 text-sm ${
              index === stepIndex
                ? "bg-arcane-blue text-white"
                : index < stepIndex
                ? "bg-forest-green text-white"
                : "bg-white text-arcane-blue"
            }`}
            onClick={() => setStepIndex(index)}
            type="button"
            disabled={!activeDraft}
          >
            {step.replace("_", " ")}
          </button>
        ))}
      </nav>

      <section className="space-y-4 rounded-lg border border-arcane-blue/30 bg-white/90 p-6 shadow">
        {!draftId && !activeDraft ? (
          <div className="space-y-4 text-sm text-gray-600">
            <p>Select or create a draft from the campaign dashboard to begin the builder.</p>
            <button
              className="rounded border border-arcane-blue px-3 py-1 text-sm text-arcane-blue hover:bg-arcane-blue hover:text-white"
              onClick={async () => {
                const draft = await createDraft.mutateAsync({});
                setSearchParams({ draft: String(draft.id) }, { replace: true });
              }}
              type="button"
            >
              Create New Draft
            </button>
          </div>
        ) : isLoadingDraft || !activeDraft || isCatalogLoading ? (
          <p className="text-sm text-gray-600">Loading builder data...</p>
        ) : currentStep === "ability_scores" ? (
          <AbilityScoreStep
            initialScores={abilityStepData}
            onChange={(payload) => handleStepUpdate("ability_scores", payload)}
            disabled={disableStepInteraction}
          />
        ) : currentStep === "origin" && catalog ? (
          <OriginStep
            species={catalog.species}
            backgrounds={catalog.backgrounds}
            languages={catalog.languages}
            initialValues={originStepData}
            onChange={(payload) => handleStepUpdate("origin", payload)}
            disabled={disableStepInteraction}
          />
        ) : currentStep === "class" && catalog ? (
          <ClassStep
            classes={catalog.classes}
            initialValues={classStepData}
            onChange={(payload) => handleStepUpdate("class", payload)}
            disabled={disableStepInteraction}
          />
        ) : currentStep === "proficiencies" && catalog ? (
          <ProficiencyStep
            classes={catalog.classes}
            skills={catalog.skills}
            tools={catalog.tools}
            classSelection={classStepData?.class}
            initialValues={profStepData}
            onChange={(payload) => handleStepUpdate("proficiencies", payload)}
            disabled={disableStepInteraction}
          />
        ) : currentStep === "equipment" && catalog ? (
          <EquipmentStep
            weapons={catalog.weapons}
            armor={catalog.armor}
            packs={catalog.packs}
            currencyTypes={catalog.currency}
            initialValues={equipmentStepData}
            onChange={(payload) => handleStepUpdate("equipment", payload)}
            disabled={disableStepInteraction}
          />
        ) : currentStep === "spells" && catalog ? (
          <SpellStep
            classId={classStepData?.class}
            characterLevel={activeDraft.starting_level}
            spells={catalog.spells}
            spellSlots={catalog.spellSlots}
            initialValues={spellStepData}
            onChange={(payload) => handleStepUpdate("spells", payload)}
            disabled={disableStepInteraction}
          />
        ) : null}

        {errorMessage ? <p className="text-sm text-ember-red">{errorMessage}</p> : null}
      </section>

      <footer className="flex justify-between">
        <button
          className="rounded border border-arcane-blue px-4 py-2 text-sm text-arcane-blue hover:bg-arcane-blue hover:text-white"
          onClick={() => navigate(-1)}
          type="button"
        >
          Exit
        </button>
        <button
          className="rounded bg-arcane-blue px-4 py-2 text-sm font-semibold text-white hover:bg-arcane-blue/90 disabled:opacity-50"
          onClick={handleContinue}
          type="button"
          disabled={updateStep.isPending || isCatalogLoading}
        >
          {stepIndex < STEP_ORDER.length - 1 ? "Continue" : "Finish"}
        </button>
      </footer>
    </div>
  );
}

export default CharacterBuilder;

