# Evaluarea limbilor — trei cazuri fictive

Cazuri care satisfac criteriile măsurate: **2/3**.

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

> The candidate has professional working proficiency in English, as stated in fact P\_EN\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> German fluency is required for daily work\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> The candidate explicitly confirms having no German language proficiency, as stated in fact P\_DE\.

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

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in English\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> The candidate has professional working proficiency in English, as stated in fact P\_EN\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> German language proficiency is an advantage\.

Prioritate: optional; matching: unknown.

Explicația brută a modelului:

> There is no conclusive evidence to determine the candidate's German language proficiency\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "German language proficiency is an advantage\.", "expected": \["confirmed\_missing", \["P\_DE"\]\], "actual": \["unknown", \[\]\]\}\]\}

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

> The candidate has professional working proficiency in English, satisfying the requirement\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.
