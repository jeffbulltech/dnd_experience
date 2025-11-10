# Character Sheet Template

Place the official **5E_CharacterSheet_Fillable.pdf** in this directory.

Example:

```
backend/templates/5E_CharacterSheet_Fillable.pdf
```

You can download the sheet from Wizards of the Coast: https://media.wizards.com/2016/dnd/downloads/5E_CharacterSheet_Fillable.pdf

The backend export endpoint (`GET /api/builder/drafts/{id}/export`) relies on this file to generate filled PDFs once a draft is finalized.
