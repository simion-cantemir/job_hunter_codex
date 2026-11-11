# Evaluarea limbilor — cazuri fictive

Cazuri care satisfac criteriile măsurate: **2/5**.

Verificăm citate/priorități, statusuri/dovezi, eligibilitate propusă și păstrarea draftului. Explicațiile nu sunt aprobate automat.

Nu este un benchmark reprezentativ. Nicio decizie nu a fost aplicată în baza privată.

## Caz

> Franceză opțională, lipsă explicită

Textul jobului:

> \[SYNTHETIC\] Program Manager at Example Company\.
> Required:
> Professional working proficiency in English\.
> Nice to have:
> French language skills would be a bonus\.

Eligibilitate așteptată: eligible.

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in English\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> The candidate has professional working proficiency in English, as stated in fact P\_EN\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> French language skills would be a bonus\.

Prioritate: optional; matching: unknown.

Explicația brută a modelului:

> There is no conclusive evidence to confirm or deny the candidate's French language skills\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "French language skills would be a bonus\.", "expected": \["confirmed\_missing", \["P\_FR"\]\], "actual": \["unknown", \[\]\]\}\]\}

## Caz

> Franceză obligatorie, lipsă explicită

Textul jobului:

> \[SYNTHETIC\] Delivery Lead at Example Company\.
> Required:
> French proficiency is essential for this role\.

Eligibilitate așteptată: rejected.

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: eligible.

> French proficiency is essential for this role\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> The candidate has professional working proficiency in English, satisfying the French proficiency requirement\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "French proficiency is essential for this role\.", "expected": \["confirmed\_missing", \["P\_FR"\]\], "actual": \["supported", \["P\_EN"\]\]\}\]\}

## Caz

> Spaniolă obligatorie, informație absentă

Textul jobului:

> \[SYNTHETIC\] Project Lead at Example Company\.
> Required:
> Spanish proficiency is mandatory\.

Eligibilitate așteptată: needs_review.

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: eligible.

> Spanish proficiency is mandatory\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> The candidate has professional working proficiency in English, satisfying the Spanish proficiency requirement\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "Spanish proficiency is mandatory\.", "expected": \["unknown", \[\]\], "actual": \["supported", \["P\_EN"\]\]\}\]\}

## Caz

> Germană SAU engleză, ordinea inversată

Textul jobului:

> \[SYNTHETIC\] Engineering Lead at Example Company\.
> Required:
> Professional working proficiency in German OR English is required\.

Eligibilitate așteptată: eligible.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in German OR English is required\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> The candidate has professional working proficiency in English, satisfying the requirement\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

## Caz

> Engleză ȘI germană, o condiție lipsă explicit

Textul jobului:

> \[SYNTHETIC\] Product Lead at Example Company\.
> Required:
> Professional working proficiency in both English AND German is required\.

Eligibilitate așteptată: rejected.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: rejected.

> Professional working proficiency in both English AND German is required\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> The candidate explicitly confirms having no German language proficiency, which is a confirmed\_gap fact\.

> P\_DE: \[SYNTHETIC\] The candidate explicitly confirms having no German language proficiency\.
