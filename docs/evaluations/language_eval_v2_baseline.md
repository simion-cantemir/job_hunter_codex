# Evaluarea limbilor — cazuri fictive

Cazuri care satisfac criteriile măsurate: **3/3**.

Verificăm citate/priorități, statusuri/dovezi, eligibilitate propusă și păstrarea draftului. Explicațiile nu sunt aprobate automat.

Nu este un benchmark reprezentativ. Nicio decizie nu a fost aplicată în baza privată.

## Caz

> Germană obligatorie, lipsă confirmată

Textul jobului:

> \[SYNTHETIC\] Engineering Manager at Fictional Company\.
> Required:
> Professional working proficiency in English\.
> German fluency is required for daily work\.

Eligibilitate așteptată: rejected.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: rejected.

> Professional working proficiency in English\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> Candidatul are o proficienșă de muncêsă profesionalâ în englezâ, demonstrată de experienȜasă\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> German fluency is required for daily work\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul nu are o proficienșâ fluíntâ în germanâ, demonstrată de confirmarea lipsei\.

> P\_DE: \[SYNTHETIC\] The candidate explicitly confirms having no German language proficiency\.

## Caz

> Germană opțională, lipsă confirmată

Textul jobului:

> \[SYNTHETIC\] Delivery Manager at Fictional Company\.
> Required:
> Professional working proficiency in English\.
> Nice to have:
> German language proficiency is an advantage\.

Eligibilitate așteptată: eligible.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in English\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> Candidatul demonstrează profesionalitatea în limba engleză\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> German language proficiency is an advantage\.

Prioritate: optional; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul nu a confirmat avântajul cunoștinței în limba germană\.

> P\_DE: \[SYNTHETIC\] The candidate explicitly confirms having no German language proficiency\.

## Caz

> Engleză SAU germană, engleză cunoscută

Textul jobului:

> \[SYNTHETIC\] Project Manager at Fictional Company\.
> Required:
> Professional working proficiency in English OR German is required\.

Eligibilitate așteptată: eligible.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in English OR German is required\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> Fapta despre proficienșa profesională în engleză este o dovÜa suficientâ pentru a satisface cerinșa\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.
