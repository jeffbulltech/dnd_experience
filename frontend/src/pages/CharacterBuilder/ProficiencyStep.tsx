import { useMemo } from "react";

import { ClassSummary, ProficiencyStepPayload, SkillDefinition, ToolDefinition } from "../../types";

type ProficiencyStepProps = {
  classes: ClassSummary[];
  skills: SkillDefinition[];
  tools: ToolDefinition[];
  classSelection?: string;
  initialValues?: ProficiencyStepPayload;
  onChange: (payload: ProficiencyStepPayload) => void;
  disabled?: boolean;
};

function ProficiencyStep({
  classes,
  skills,
  tools,
  classSelection,
  initialValues,
  onChange,
  disabled = false
}: ProficiencyStepProps): JSX.Element {
  const selectedSkills = initialValues?.skills ?? [];
  const selectedTools = initialValues?.tools ?? [];
  const expertise = initialValues?.expertise ?? [];

  const classOptions = useMemo(() => classes, [classes]);
  const selectedClass = classOptions.find((klass) => klass.id === classSelection);
  const maxSkills = selectedClass?.skill_choices?.count ?? 0;
  const classSkillOptions = selectedClass?.skill_choices?.options ?? [];

  const toggleSelection = (list: string[], value: string): string[] => {
    const set = new Set(list);
    if (set.has(value)) {
      set.delete(value);
    } else {
      set.add(value);
    }
    return Array.from(set);
  };

  const handleSkillToggle = (value: string) => {
    let nextSkills = toggleSelection(selectedSkills, value);
    if (maxSkills && nextSkills.length > maxSkills) {
      return;
    }
    onChange({
      skills: nextSkills,
      tools: selectedTools,
      expertise,
    });
  };

  const handleToolToggle = (value: string) => {
    const nextTools = toggleSelection(selectedTools, value);
    onChange({
      skills: selectedSkills,
      tools: nextTools,
      expertise,
    });
  };

  const handleExpertiseToggle = (value: string) => {
    if (!selectedSkills.includes(value)) return;
    const nextExpertise = toggleSelection(expertise, value);
    onChange({
      skills: selectedSkills,
      tools: selectedTools,
      expertise: nextExpertise,
    });
  };

  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-arcane-blue">Proficiencies</h2>
        <p className="text-sm text-gray-600">
          Choose skill and tool proficiencies granted by your class, species, and background. You may also select
          expertise from proficient skills when allowed.
        </p>
      </header>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-arcane-blue">Skill Proficiencies</h3>
        <p className="text-xs text-gray-600">Select up to {maxSkills || "the allowed number"} skills from your class options.</p>
        <div className="flex flex-wrap gap-2">
          {classSkillOptions.map((skillId) => {
            const skill = skills.find((entry) => entry.id === skillId);
            if (!skill) return null;
            const selected = selectedSkills.includes(skill.id);
            return (
              <button
                key={skill.id}
                className={`rounded border px-3 py-1 text-xs ${selected ? "border-arcane-blue bg-arcane-blue text-white" : "border-arcane-blue/30"}`}
                onClick={() => handleSkillToggle(skill.id)}
                type="button"
                disabled={disabled}
              >
                {skill.name} ({skill.ability.toUpperCase()})
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-arcane-blue">Tool Proficiencies</h3>
        <div className="flex flex-wrap gap-2">
          {tools.map((tool) => {
            const selected = selectedTools.includes(tool.id);
            return (
              <button
                key={tool.id}
                className={`rounded border px-3 py-1 text-xs ${selected ? "border-forest-green bg-forest-green text-white" : "border-forest-green/30"}`}
                onClick={() => handleToolToggle(tool.id)}
                type="button"
                disabled={disabled}
              >
                {tool.name}
              </button>
            );
          })}
        </div>
      </div>

      {selectedSkills.length > 0 ? (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-arcane-blue">Expertise</h3>
          <p className="text-xs text-gray-600">Select skills in which you gain double proficiency bonus.</p>
          <div className="flex flex-wrap gap-2">
            {selectedSkills.map((skillId) => {
              const skill = skills.find((entry) => entry.id === skillId);
              if (!skill) return null;
              const selected = expertise.includes(skill.id);
              return (
                <button
                  key={skill.id}
                  className={`rounded border px-3 py-1 text-xs ${selected ? "border-amber-500 bg-amber-200" : "border-amber-500/40"}`}
                  onClick={() => handleExpertiseToggle(skill.id)}
                  type="button"
                  disabled={disabled}
                >
                  {skill.name}
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default ProficiencyStep;
