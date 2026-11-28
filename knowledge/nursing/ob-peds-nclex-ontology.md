---
title: "OB + Peds Final Exam NCLEX Study Guide Ontology"
source_document: "OB + Peds Final Exam NCLEX Study Guide.pdf"
exam_date: "Monday, December 7"
total_items: 100
item_breakdown:
  ob_maternal_newborn: 52
  pediatrics: 34
  cross_cutting: 14
textbook_reference: "Silbert-Flagg, 9th ed."
practice_questions_count: 155
canvas_worksheets_count: 7
study_schedule_days: 18
branch_target: "editor-test"
---

# OB + Peds Final Exam NCLEX Study Guide Ontology

## 1. Exam Blueprint & Study Rules
- **Exam Weighting**: 100 total items on Monday, December 7 (52 OB/Maternal-Newborn, 34 Pediatrics, 14 Cross-cutting; pharmacology [15], alternate format [8], and overlapping categories count across domains).
- **Target Score**: 90+ (allows missing up to 10 items; prioritize Newborn [18], Pharm/dosage calc [15], Pregnancy [11], and Alternate format [8]).
- **Conflict Resolution Rule**: When lecture notes and Silbert-Flagg 9th ed. differ, answer the exam using the lecture.
- **Clinical Priority Rule**: Assess before acting unless an active emergency is already occurring.

## 2. Core Ontology Classes
- **ExamBlueprint**: Exam item breakdown, target score, schedule window, and decision rules.
- **ClinicalDomain**: Top-level domain (`OB / Maternal-Newborn`, `Pediatrics`, `Cross-Cutting`).
- **TopicModule**: Study sections 1–23 mapped to lectures, textbook chapters, Canvas worksheets, and practice questions.
- **ClinicalEntity**: Conditions, states, stages, procedures, or legal/cultural constructs within a module.
- **ClinicalFinding**: Signs, symptoms, vital signs, labs, and monitoring patterns (normal vs. warning/red flag).
- **NursingIntervention**: Priority/first actions, contraindicated actions, ongoing monitoring, and client/family teaching.
- **MedicationEntity**: OB, newborn, pediatric, and women's health drugs with nursing checks, red flags, and antidotes.
- **DosageCalculationRule**: Formulas and conversions for medications, IV rates, fluids, diaper output, Nagele's rule, and G-TPAL.
- **AssessmentArtifact**: 7 Canvas worksheets, 155 practice questions, 18-day countdown schedule, night-before cheat sheet, and answer key rationales.
- **ProvenanceRecord**: Source mapping across lectures, Silbert-Flagg 9th ed., and plain-English/memory-trick aids.

## 3. Section & Module Taxonomy (Sections 1–23)
1. **Normal Pregnancy & Prenatal Care** (11 items; OB 1 & 2, Ch. 7, 9–13; Worksheets #1 & #2; Q1.1–Q1.14)
2. **Complications of Pregnancy** (part of Preg/L&D; OB 5, Ch. 20–22; Worksheet #6; Q2.1–Q2.14)
3. **Labor & Delivery + Complications** (6 items; OB 1 & 2 + OB 6, Ch. 14–16, 23–24; Worksheets #3, #4, #6; Q3.1–Q3.10)
4. **Postpartum + PP Complications** (7 items; OB 3 + OB 7, Ch. 17, 25; Worksheet #4; Q4.1–Q4.9)
5. **The Newborn: Healthy & High-Risk** (18 items; OB 4 + OB 8, Ch. 18–19, 26–27; Worksheets #5 & #7; Q5.1–Q5.16)
6. **Family Planning** (6 items; Silbert-Flagg Ch. 6, pp. 104–130; Q6.1–Q6.8)
7. **Women's Health** (4 items; Women's Health lecture, Ch. 5, 8, 47; Q7.1–Q7.6)
8. **Growth & Development + the Hospitalized Child** (4 items; Peds 1, Ch. 28–33, 36–38; Q8.1–Q8.6)
9. **Respiratory Disorders** (3 items; Peds 2, Ch. 40; Q9.1–Q9.5)
10. **Cardiac Disorders** (3 items; Peds 3, Ch. 41; Q10.1–Q10.5)
11. **Infectious & Immune Disorders** (3 items; Peds 4, Ch. 34, 42–43; Q11.1–Q11.5)
12. **Gastrointestinal Disorders** (6 items; Peds 6, Ch. 45; Q12.1–Q12.8)
13. **Hematologic Disorders** (2 items; Peds 5, Ch. 44; Q13.1–Q13.4)
14. **Renal, Reproductive & Endocrine** (3 items; Peds 7–9, Ch. 46–48; Q14.1–Q14.5)
15. **Neuro & Sensory Disorders** (2 items; Peds 10 & 11, Ch. 49–50; Q15.1–Q15.4)
16. **Musculoskeletal & Trauma** (1 + 1 items; Peds 12 & 13, Ch. 51–52; Q16.1–Q16.3)
17. **Childhood Cancer** (3 items; Peds 14, Ch. 53; Q17.1–Q17.4)
18. **Mandated Reporting & Maltreatment** (2 items; Ch. 55 + OB IPV screening; Q18.1–Q18.3)
19. **Pharmacology Cards + Dosage Calc** (15 items; Q19.1–Q19.15)
20. **Lab Values & Cultural Care** (labs + 1 item; Ch. 2; Q20.1–Q20.3)
21. **Alternate-Format Practice** (8 items; SATA, ordered response, hot spot, exhibit, fill-in, matrix; Q21.1–Q21.8)
22. **Countdown Study Schedule** (18 days: Thu 11/19 to Mon 12/7)
23. **Night-Before Cheat Sheet** (1-page rapid review + Answer Key & Rationales)

## 4. Core Semantic Relationships
- `TopicModule` **belongsToDomain** `ClinicalDomain`
- `TopicModule` **mapsToSource** `ProvenanceRecord`
- `ClinicalEntity` **hasFinding** `ClinicalFinding`
- `ClinicalEntity` **requiresIntervention** `NursingIntervention`
- `NursingIntervention` **contraindicates** `ClinicalFinding` or `ClinicalEntity`
- `MedicationEntity` **treatsOrPrevents** `ClinicalEntity`
- `MedicationEntity` **hasRedFlagOrAntidote** `ClinicalFinding` or `MedicationEntity`
- `DosageCalculationRule` **appliesTo** `MedicationEntity` or `ClinicalEntity`
- `AssessmentArtifact` **evaluates** `TopicModule` and `ClinicalEntity`
