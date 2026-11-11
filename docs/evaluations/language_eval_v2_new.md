# Evaluarea limbilor — cazuri fictive

Cazuri care satisfac criteriile măsurate: **3/5**.

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

Criterii măsurate: trecute.

Eligibilitate propusă de flux: eligible.

> Professional working proficiency in English\.

Prioritate: mandatory; matching: supported.

Explicația brută a modelului:

> Candidatul demonstrează profesionistă working proficiency în engleză\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

> French language skills would be a bonus\.

Prioritate: optional; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul confirmă explicit că nu vorbește franceză\.

> P\_FR: \[SYNTHETIC\] The candidate explicitly states that they do not speak French\.

## Caz

> Franceză obligatorie, lipsă explicită

Textul jobului:

> \[SYNTHETIC\] Delivery Lead at Example Company\.
> Required:
> French proficiency is essential for this role\.

Eligibilitate așteptată: rejected.

Criterii măsurate: trecute.

Eligibilitate propusă de flux: rejected.

> French proficiency is essential for this role\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul nu a confirmat că vorbăște franceză, deși a declarat că nu vorbește niciun alt limbaj\.

> P\_FR: \[SYNTHETIC\] The candidate explicitly states that they do not speak French\.

## Caz

> Spaniolă obligatorie, informație absentă

Textul jobului:

> \[SYNTHETIC\] Project Lead at Example Company\.
> Required:
> Spanish proficiency is mandatory\.

Eligibilitate așteptată: needs_review.

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: rejected.

> Spanish proficiency is mandatory\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul confirmă explicit că nu are cunoștințe în germană și franceză, deci nu îndeplinește cerința de cunoștințe lingvistice\.

> P\_DE: \[SYNTHETIC\] The candidate explicitly confirms having no German language proficiency\.

> P\_FR: \[SYNTHETIC\] The candidate explicitly states that they do not speak French\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "Spanish proficiency is mandatory\.", "expected": \["unknown", \[\]\], "actual": \["confirmed\_missing", \["P\_DE", "P\_FR"\]\]\}\]\}

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

> Candidatul are profesionistă working proficiency în engleză, ceea ce demonstrează întreaga cerință\.

> P\_EN: \[SYNTHETIC\] The candidate has professional working proficiency in English\.

## Caz

> Engleză ȘI germană, o condiție lipsă explicit

Textul jobului:

> \[SYNTHETIC\] Product Lead at Example Company\.
> Required:
> Professional working proficiency in both English AND German is required\.

Eligibilitate așteptată: rejected.

Criterii măsurate: diferențe identificate.

Eligibilitate propusă de flux: rejected.

> Professional working proficiency in both English AND German is required\.

Prioritate: mandatory; matching: confirmed_missing.

Explicația brută a modelului:

> Candidatul confirmă explicit că nu are competență în germană și franceză\.

> P\_DE: \[SYNTHETIC\] The candidate explicitly confirms having no German language proficiency\.

> P\_FR: \[SYNTHETIC\] The candidate explicitly states that they do not speak French\.

Diferențe pentru revizuire:

> \{"missing": \[\], "unexpected": \[\], "matching": \[\{"quote": "Professional working proficiency in both English AND German is required\.", "expected": \["confirmed\_missing", \["P\_DE"\]\], "actual": \["confirmed\_missing", \["P\_DE", "P\_FR"\]\]\}\]\}
