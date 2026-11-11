# Reguli de limbă — verificare pe cele opt cazuri fictive

Criterii măsurate trecute: **8/8**.

Intrările structurate sunt adnotate de agent, nu extrase automat și nu aprobate de utilizator. Rezultatul măsoară regulile Python pe aceste intrări, nu precizia unui LLM.

Nu au fost apelate modele și nu au fost aplicate decizii sau modificate baze private.

## Caz

> Germană obligatorie, lipsă confirmată

Propunere LLM salvată: rejected. Propunere după reguli: rejected.

> R1: supported — P\_EN

> Evaluare deterministă pe date structurate\. Engleză: Nivel profesional confirmat\. Cerința este susținută de dovezile indicate\.

> R2: confirmed\_missing — P\_DE

> Evaluare deterministă pe date structurate\. Germană: Lipsă declarată explicit\. Lipsa declarată explicit împiedică satisfacerea acestei condiții\.

## Caz

> Germană opțională, lipsă confirmată

Propunere LLM salvată: eligible. Propunere după reguli: eligible.

> R1: supported — P\_EN

> Evaluare deterministă pe date structurate\. Engleză: Nivel profesional confirmat\. Cerința este susținută de dovezile indicate\.

> R2: confirmed\_missing — P\_DE

> Evaluare deterministă pe date structurate\. Germană: Lipsă declarată explicit\. Lipsa declarată explicit împiedică satisfacerea acestei condiții\.

## Caz

> Engleză SAU germană, engleză cunoscută

Propunere LLM salvată: eligible. Propunere după reguli: eligible.

> R1: supported — P\_EN

> Evaluare deterministă pe date structurate\. Engleză: Nivel profesional confirmat; Germană: Lipsă declarată explicit\. Cerința este susținută de dovezile indicate\.

## Caz

> Franceză opțională, lipsă explicită

Propunere LLM salvată: eligible. Propunere după reguli: eligible.

> R1: supported — P\_EN

> Evaluare deterministă pe date structurate\. Engleză: Nivel profesional confirmat\. Cerința este susținută de dovezile indicate\.

> R2: confirmed\_missing — P\_FR

> Evaluare deterministă pe date structurate\. Franceză: Lipsă declarată explicit\. Lipsa declarată explicit împiedică satisfacerea acestei condiții\.

## Caz

> Franceză obligatorie, lipsă explicită

Propunere LLM salvată: rejected. Propunere după reguli: rejected.

> R1: confirmed\_missing — P\_FR

> Evaluare deterministă pe date structurate\. Franceză: Lipsă declarată explicit\. Lipsa declarată explicit împiedică satisfacerea acestei condiții\.

## Caz

> Spaniolă obligatorie, informație absentă

Propunere LLM salvată: rejected. Propunere după reguli: needs_review.

> R1: unknown — fără dovezi concludente

> Evaluare deterministă pe date structurate\. Spaniolă: Necunoscut\. Informațiile sau condiția sunt neclare; necesită clarificare, fără a presupune o lipsă\.

## Caz

> Germană SAU engleză, ordinea inversată

Propunere LLM salvată: eligible. Propunere după reguli: eligible.

> R1: supported — P\_EN

> Evaluare deterministă pe date structurate\. Germană: Lipsă declarată explicit; Engleză: Nivel profesional confirmat\. Cerința este susținută de dovezile indicate\.

## Caz

> Engleză ȘI germană, o condiție lipsă explicit

Propunere LLM salvată: rejected. Propunere după reguli: rejected.

> R1: confirmed\_missing — P\_DE

> Evaluare deterministă pe date structurate\. Engleză: Nivel profesional confirmat; Germană: Lipsă declarată explicit\. Lipsa declarată explicit împiedică satisfacerea acestei condiții\.
