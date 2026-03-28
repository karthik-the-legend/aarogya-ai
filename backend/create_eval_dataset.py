import json
import os

dataset = {
    "metadata": {
        "total_queries"    : 50,
        "total_triage"     : 20,
        "diseases"         : 10,
        "questions_per_disease": 5,
        "created_by"       : "Karthik K S",
        "purpose"          : "RAGAS evaluation — manual ground truth from WHO/CDC/NIH PDFs"
    },

    "queries": [

        # ── DENGUE (5 questions) ─────────────────────────────────
        {
            "id"          : "Q001",
            "disease"     : "Dengue",
            "category"    : "symptoms",
            "query"       : "What are the symptoms of dengue fever?",
            "source_pdf"  : "01_who_dengue.pdf",
            "ground_truth": "Dengue symptoms include sudden high fever, severe headache, pain behind the eyes, muscle and joint pains, nausea, vomiting, swollen glands, and rash. Symptoms appear 4-10 days after infection.",
            "key_terms"   : ["fever", "headache", "rash", "muscle pain", "joint pain"]
        },
        {
            "id"          : "Q002",
            "disease"     : "Dengue",
            "category"    : "treatment",
            "query"       : "Can I take ibuprofen for dengue fever?",
            "source_pdf"  : "06_cdc_dengue_clinical.pdf",
            "ground_truth": "Ibuprofen and aspirin should be AVOIDED in dengue as they can increase the risk of bleeding. Use paracetamol (acetaminophen) only for fever and pain relief.",
            "key_terms"   : ["avoid", "ibuprofen", "paracetamol", "bleeding"]
        },
        {
            "id"          : "Q003",
            "disease"     : "Dengue",
            "category"    : "emergency",
            "query"       : "What are warning signs of severe dengue?",
            "source_pdf"  : "06_cdc_dengue_clinical.pdf",
            "ground_truth": "Warning signs include severe abdominal pain, persistent vomiting, bleeding from gums or nose, blood in urine or stool, rapid breathing, fatigue, and restlessness. These require immediate hospital care.",
            "key_terms"   : ["bleeding", "abdominal pain", "vomiting", "hospital"]
        },
        {
            "id"          : "Q004",
            "disease"     : "Dengue",
            "category"    : "prevention",
            "query"       : "How can I prevent dengue fever?",
            "source_pdf"  : "01_who_dengue.pdf",
            "ground_truth": "Prevent dengue by eliminating mosquito breeding sites, using mosquito repellents, wearing long-sleeved clothes, using mosquito nets, and ensuring water containers are covered.",
            "key_terms"   : ["mosquito", "repellent", "breeding", "prevention"]
        },
        {
            "id"          : "Q005",
            "disease"     : "Dengue",
            "category"    : "transmission",
            "query"       : "How is dengue transmitted?",
            "source_pdf"  : "01_who_dengue.pdf",
            "ground_truth": "Dengue is transmitted through the bite of infected Aedes mosquitoes, primarily Aedes aegypti. It is not spread directly from person to person.",
            "key_terms"   : ["mosquito", "Aedes", "bite", "transmitted"]
        },

        # ── MALARIA (5 questions) ────────────────────────────────
        {
            "id"          : "Q006",
            "disease"     : "Malaria",
            "category"    : "symptoms",
            "query"       : "What are the symptoms of malaria?",
            "source_pdf"  : "02_who_malaria.pdf",
            "ground_truth": "Malaria symptoms include fever, chills, headache, muscle aches, fatigue, nausea, and vomiting. Symptoms appear 10-15 days after a mosquito bite.",
            "key_terms"   : ["fever", "chills", "headache", "fatigue"]
        },
        {
            "id"          : "Q007",
            "disease"     : "Malaria",
            "category"    : "treatment",
            "query"       : "How is malaria treated?",
            "source_pdf"  : "07_cdc_malaria_clinical.pdf",
            "ground_truth": "Malaria is treated with antimalarial medicines. The type depends on the parasite species. Common treatments include artemisinin-based combination therapies (ACTs) for falciparum malaria.",
            "key_terms"   : ["antimalarial", "artemisinin", "treatment", "medicines"]
        },
        {
            "id"          : "Q008",
            "disease"     : "Malaria",
            "category"    : "prevention",
            "query"       : "How can malaria be prevented?",
            "source_pdf"  : "02_who_malaria.pdf",
            "ground_truth": "Malaria prevention includes sleeping under insecticide-treated nets, indoor residual spraying, antimalarial drugs for travelers, and eliminating standing water.",
            "key_terms"   : ["nets", "insecticide", "prevention", "spraying"]
        },
        {
            "id"          : "Q009",
            "disease"     : "Malaria",
            "category"    : "transmission",
            "query"       : "How is malaria transmitted?",
            "source_pdf"  : "02_who_malaria.pdf",
            "ground_truth": "Malaria is transmitted through the bite of infected female Anopheles mosquitoes. It can also spread through blood transfusions and shared needles.",
            "key_terms"   : ["Anopheles", "mosquito", "bite", "blood"]
        },
        {
            "id"          : "Q010",
            "disease"     : "Malaria",
            "category"    : "emergency",
            "query"       : "What are signs of severe malaria?",
            "source_pdf"  : "07_cdc_malaria_clinical.pdf",
            "ground_truth": "Severe malaria signs include high fever above 40C, seizures, loss of consciousness, severe anaemia, difficulty breathing, and organ failure. Requires immediate medical attention.",
            "key_terms"   : ["seizures", "consciousness", "severe", "emergency"]
        },

        # ── TYPHOID (5 questions) ────────────────────────────────
        {
            "id"          : "Q011",
            "disease"     : "Typhoid",
            "category"    : "symptoms",
            "query"       : "What are symptoms of typhoid fever?",
            "source_pdf"  : "05_cdc_typhoid.pdf",
            "ground_truth": "Typhoid symptoms include sustained fever up to 40C, weakness, stomach pain, headache, diarrhoea or constipation, and sometimes a rash of flat rose-coloured spots.",
            "key_terms"   : ["fever", "stomach pain", "headache", "weakness"]
        },
        {
            "id"          : "Q012",
            "disease"     : "Typhoid",
            "category"    : "transmission",
            "query"       : "How does typhoid spread?",
            "source_pdf"  : "05_cdc_typhoid.pdf",
            "ground_truth": "Typhoid spreads through contaminated food and water with Salmonella Typhi bacteria. It also spreads through contact with an infected person.",
            "key_terms"   : ["contaminated", "water", "food", "Salmonella"]
        },
        {
            "id"          : "Q013",
            "disease"     : "Typhoid",
            "category"    : "prevention",
            "query"       : "How can typhoid be prevented?",
            "source_pdf"  : "05_cdc_typhoid.pdf",
            "ground_truth": "Typhoid prevention includes vaccination, drinking safe water, eating properly cooked food, good hand hygiene, and avoiding raw vegetables in endemic areas.",
            "key_terms"   : ["vaccination", "water", "hygiene", "prevention"]
        },
        {
            "id"          : "Q014",
            "disease"     : "Typhoid",
            "category"    : "treatment",
            "query"       : "How is typhoid treated?",
            "source_pdf"  : "05_cdc_typhoid.pdf",
            "ground_truth": "Typhoid is treated with antibiotics. Fluoroquinolones and cephalosporins are commonly used. Rest and adequate hydration are also important.",
            "key_terms"   : ["antibiotics", "treatment", "hydration"]
        },
        {
            "id"          : "Q015",
            "disease"     : "Typhoid",
            "category"    : "emergency",
            "query"       : "What are complications of untreated typhoid?",
            "source_pdf"  : "05_cdc_typhoid.pdf",
            "ground_truth": "Untreated typhoid can lead to intestinal perforation, internal bleeding, inflammation of heart muscles, pneumonia, and can be fatal without treatment.",
            "key_terms"   : ["perforation", "bleeding", "complications", "fatal"]
        },

        # ── TUBERCULOSIS (5 questions) ───────────────────────────
        {
            "id"          : "Q016",
            "disease"     : "Tuberculosis",
            "category"    : "symptoms",
            "query"       : "What are symptoms of tuberculosis?",
            "source_pdf"  : "03_who_tuberculosis.pdf",
            "ground_truth": "TB symptoms include persistent cough lasting 3+ weeks, coughing blood, chest pain, weakness, weight loss, fever, night sweats, and loss of appetite.",
            "key_terms"   : ["cough", "blood", "fever", "weight loss", "night sweats"]
        },
        {
            "id"          : "Q017",
            "disease"     : "Tuberculosis",
            "category"    : "transmission",
            "query"       : "Is tuberculosis contagious?",
            "source_pdf"  : "03_who_tuberculosis.pdf",
            "ground_truth": "Yes, TB is contagious. It spreads through the air when an infected person coughs, sneezes, or speaks. Close and prolonged contact increases risk.",
            "key_terms"   : ["contagious", "airborne", "cough", "spreads"]
        },
        {
            "id"          : "Q018",
            "disease"     : "Tuberculosis",
            "category"    : "treatment",
            "query"       : "How long is TB treatment?",
            "source_pdf"  : "03_who_tuberculosis.pdf",
            "ground_truth": "TB treatment typically lasts 6 months with a combination of antibiotics. The standard regimen uses isoniazid, rifampicin, pyrazinamide, and ethambutol.",
            "key_terms"   : ["6 months", "antibiotics", "isoniazid", "rifampicin"]
        },
        {
            "id"          : "Q019",
            "disease"     : "Tuberculosis",
            "category"    : "prevention",
            "query"       : "How can TB be prevented?",
            "source_pdf"  : "03_who_tuberculosis.pdf",
            "ground_truth": "TB prevention includes BCG vaccination for children, identifying and treating active cases, improving ventilation, and completing full antibiotic courses.",
            "key_terms"   : ["BCG", "vaccination", "prevention", "ventilation"]
        },
        {
            "id"          : "Q020",
            "disease"     : "Tuberculosis",
            "category"    : "emergency",
            "query"       : "When should a TB patient go to hospital immediately?",
            "source_pdf"  : "03_who_tuberculosis.pdf",
            "ground_truth": "Seek immediate care if coughing blood, having difficulty breathing, high fever, or chest pain. These may indicate severe TB or complications.",
            "key_terms"   : ["coughing blood", "breathing", "emergency", "hospital"]
        },

        # ── CHOLERA (5 questions) ────────────────────────────────
        {
            "id"          : "Q021",
            "disease"     : "Cholera",
            "category"    : "symptoms",
            "query"       : "What are signs of cholera?",
            "source_pdf"  : "04_who_cholera.pdf",
            "ground_truth": "Cholera causes sudden watery diarrhoea described as rice-water stools, vomiting, and leg cramps. Severe dehydration can develop rapidly and be fatal.",
            "key_terms"   : ["diarrhoea", "watery", "vomiting", "dehydration"]
        },
        {
            "id"          : "Q022",
            "disease"     : "Cholera",
            "category"    : "treatment",
            "query"       : "How is cholera treated?",
            "source_pdf"  : "04_who_cholera.pdf",
            "ground_truth": "Cholera is treated with oral rehydration salts (ORS) to replace lost fluids. Severe cases need IV fluids. Antibiotics can shorten illness duration.",
            "key_terms"   : ["ORS", "rehydration", "fluids", "antibiotics"]
        },
        {
            "id"          : "Q023",
            "disease"     : "Cholera",
            "category"    : "prevention",
            "query"       : "How can cholera be prevented?",
            "source_pdf"  : "04_who_cholera.pdf",
            "ground_truth": "Cholera prevention includes drinking safe treated water, proper sanitation, hand washing with soap, cooking food thoroughly, and cholera vaccination in endemic areas.",
            "key_terms"   : ["water", "sanitation", "hand washing", "vaccination"]
        },
        {
            "id"          : "Q024",
            "disease"     : "Cholera",
            "category"    : "transmission",
            "query"       : "How does cholera spread?",
            "source_pdf"  : "04_who_cholera.pdf",
            "ground_truth": "Cholera spreads through contaminated water and food. The Vibrio cholerae bacteria enters through the mouth and multiplies in the intestine.",
            "key_terms"   : ["contaminated", "water", "Vibrio", "bacteria"]
        },
        {
            "id"          : "Q025",
            "disease"     : "Cholera",
            "category"    : "emergency",
            "query"       : "When is cholera an emergency?",
            "source_pdf"  : "04_who_cholera.pdf",
            "ground_truth": "Cholera becomes emergency when severe dehydration occurs — signs include sunken eyes, dry mouth, no urination, and confusion. IV fluids needed immediately.",
            "key_terms"   : ["dehydration", "emergency", "IV fluids", "severe"]
        },

        # ── INFLUENZA/FLU (5 questions) ──────────────────────────
        {
            "id"          : "Q026",
            "disease"     : "Influenza",
            "category"    : "symptoms",
            "query"       : "What are symptoms of flu?",
            "source_pdf"  : "08_cdc_influenza.pdf",
            "ground_truth": "Flu symptoms include sudden fever, chills, muscle aches, headache, fatigue, dry cough, sore throat, and runny nose. Symptoms are more severe than common cold.",
            "key_terms"   : ["fever", "muscle aches", "fatigue", "cough"]
        },
        {
            "id"          : "Q027",
            "disease"     : "Influenza",
            "category"    : "treatment",
            "query"       : "Can flu be treated with antibiotics?",
            "source_pdf"  : "08_cdc_influenza.pdf",
            "ground_truth": "No, antibiotics do not work against flu as it is caused by a virus. Antiviral medications like oseltamivir (Tamiflu) can reduce severity if taken early.",
            "key_terms"   : ["antibiotics", "virus", "antiviral", "oseltamivir"]
        },
        {
            "id"          : "Q028",
            "disease"     : "Influenza",
            "category"    : "prevention",
            "query"       : "How can flu be prevented?",
            "source_pdf"  : "08_cdc_influenza.pdf",
            "ground_truth": "Annual flu vaccination is the best prevention. Also wash hands frequently, avoid close contact with sick people, and cover coughs and sneezes.",
            "key_terms"   : ["vaccination", "vaccine", "prevention", "hand washing"]
        },
        {
            "id"          : "Q029",
            "disease"     : "Influenza",
            "category"    : "transmission",
            "query"       : "How does flu spread?",
            "source_pdf"  : "08_cdc_influenza.pdf",
            "ground_truth": "Flu spreads through respiratory droplets when infected people cough, sneeze, or talk. It can also spread by touching contaminated surfaces then touching the face.",
            "key_terms"   : ["droplets", "cough", "sneeze", "spreads"]
        },
        {
            "id"          : "Q030",
            "disease"     : "Influenza",
            "category"    : "emergency",
            "query"       : "When should I see a doctor for flu?",
            "source_pdf"  : "08_cdc_influenza.pdf",
            "ground_truth": "See a doctor if you have difficulty breathing, persistent chest pain, confusion, severe vomiting, or if high fever does not improve after 3 days.",
            "key_terms"   : ["doctor", "breathing", "chest pain", "emergency"]
        },

        # ── FEVER (5 questions) ──────────────────────────────────
        {
            "id"          : "Q031",
            "disease"     : "Fever",
            "category"    : "symptoms",
            "query"       : "What temperature is considered a fever?",
            "source_pdf"  : "09_ncbi_fever.pdf",
            "ground_truth": "A fever is generally defined as body temperature above 38°C (100.4°F). Normal body temperature is around 37°C (98.6°F).",
            "key_terms"   : ["38", "temperature", "fever", "100.4"]
        },
        {
            "id"          : "Q032",
            "disease"     : "Fever",
            "category"    : "treatment",
            "query"       : "How to manage fever at home?",
            "source_pdf"  : "09_ncbi_fever.pdf",
            "ground_truth": "Manage fever at home by resting, drinking plenty of fluids, taking paracetamol or ibuprofen as directed, wearing light clothing, and using cool compresses.",
            "key_terms"   : ["fluids", "paracetamol", "rest", "cool"]
        },
        {
            "id"          : "Q033",
            "disease"     : "Fever",
            "category"    : "emergency",
            "query"       : "When is fever dangerous?",
            "source_pdf"  : "09_ncbi_fever.pdf",
            "ground_truth": "Fever is dangerous when above 39.4°C (103°F) in adults, or if accompanied by severe headache, stiff neck, confusion, rash, difficulty breathing, or lasts more than 3 days.",
            "key_terms"   : ["103", "dangerous", "severe", "3 days"]
        },
        {
            "id"          : "Q034",
            "disease"     : "Fever",
            "category"    : "prevention",
            "query"       : "How to prevent getting fever?",
            "source_pdf"  : "09_ncbi_fever.pdf",
            "ground_truth": "Prevent fever by washing hands regularly, getting vaccinations, avoiding close contact with sick people, and maintaining good hygiene.",
            "key_terms"   : ["hand washing", "vaccination", "hygiene", "prevention"]
        },
        {
            "id"          : "Q035",
            "disease"     : "Fever",
            "category"    : "transmission",
            "query"       : "What causes fever in adults?",
            "source_pdf"  : "09_ncbi_fever.pdf",
            "ground_truth": "Common causes of fever include viral infections like flu and cold, bacterial infections, inflammatory conditions, and certain medications.",
            "key_terms"   : ["infection", "viral", "bacterial", "causes"]
        },

        # ── DIARRHOEA (5 questions) ──────────────────────────────
        {
            "id"          : "Q036",
            "disease"     : "Diarrhoea",
            "category"    : "symptoms",
            "query"       : "What are symptoms of diarrhoea?",
            "source_pdf"  : "10_ncbi_diarrhoea.pdf",
            "ground_truth": "Diarrhoea is characterised by loose, watery stools three or more times a day, stomach cramps, nausea, and sometimes fever and blood in stools.",
            "key_terms"   : ["loose", "watery", "stools", "cramps"]
        },
        {
            "id"          : "Q037",
            "disease"     : "Diarrhoea",
            "category"    : "treatment",
            "query"       : "How to treat diarrhoea with rehydration?",
            "source_pdf"  : "10_ncbi_diarrhoea.pdf",
            "ground_truth": "Treat diarrhoea with oral rehydration solution (ORS) to replace lost fluids and electrolytes. Drink small sips frequently. Avoid sugary drinks and alcohol.",
            "key_terms"   : ["ORS", "rehydration", "electrolytes", "fluids"]
        },
        {
            "id"          : "Q038",
            "disease"     : "Diarrhoea",
            "category"    : "prevention",
            "query"       : "How to prevent diarrhoea?",
            "source_pdf"  : "10_ncbi_diarrhoea.pdf",
            "ground_truth": "Prevent diarrhoea by drinking safe water, washing hands before eating, cooking food thoroughly, and avoiding raw or undercooked food.",
            "key_terms"   : ["water", "hand washing", "food", "prevention"]
        },
        {
            "id"          : "Q039",
            "disease"     : "Diarrhoea",
            "category"    : "emergency",
            "query"       : "When is diarrhoea an emergency?",
            "source_pdf"  : "10_ncbi_diarrhoea.pdf",
            "ground_truth": "Seek emergency care if diarrhoea lasts more than 2 days, contains blood, is accompanied by high fever, or if signs of dehydration appear like dry mouth and no urination.",
            "key_terms"   : ["blood", "dehydration", "emergency", "2 days"]
        },
        {
            "id"          : "Q040",
            "disease"     : "Diarrhoea",
            "category"    : "transmission",
            "query"       : "What causes diarrhoea?",
            "source_pdf"  : "10_ncbi_diarrhoea.pdf",
            "ground_truth": "Diarrhoea is caused by viruses like rotavirus, bacteria like E.coli and salmonella, parasites, contaminated food and water, and sometimes medications.",
            "key_terms"   : ["virus", "bacteria", "contaminated", "causes"]
        },

        # ── COMMON COLD (5 questions) ────────────────────────────
        {
            "id"          : "Q041",
            "disease"     : "Common Cold",
            "category"    : "symptoms",
            "query"       : "What are symptoms of common cold?",
            "source_pdf"  : "11_ncbi_common_cold.pdf",
            "ground_truth": "Common cold symptoms include runny or stuffy nose, sore throat, cough, mild fever, sneezing, mild body aches, and generally feeling unwell.",
            "key_terms"   : ["runny nose", "sore throat", "cough", "sneezing"]
        },
        {
            "id"          : "Q042",
            "disease"     : "Common Cold",
            "category"    : "treatment",
            "query"       : "How to treat common cold at home?",
            "source_pdf"  : "11_ncbi_common_cold.pdf",
            "ground_truth": "Common cold has no cure but symptoms can be managed with rest, fluids, honey for cough, nasal decongestants, and paracetamol for fever and aches.",
            "key_terms"   : ["rest", "fluids", "no cure", "symptomatic"]
        },
        {
            "id"          : "Q043",
            "disease"     : "Common Cold",
            "category"    : "prevention",
            "query"       : "How to prevent catching a cold?",
            "source_pdf"  : "11_ncbi_common_cold.pdf",
            "ground_truth": "Prevent cold by washing hands frequently, avoiding touching face, staying away from sick people, and maintaining good immunity through diet and exercise.",
            "key_terms"   : ["hand washing", "prevention", "immunity"]
        },
        {
            "id"          : "Q044",
            "disease"     : "Common Cold",
            "category"    : "transmission",
            "query"       : "How does common cold spread?",
            "source_pdf"  : "11_ncbi_common_cold.pdf",
            "ground_truth": "Cold spreads through respiratory droplets from coughing and sneezing, and by touching contaminated surfaces then touching eyes, nose, or mouth.",
            "key_terms"   : ["droplets", "cough", "surfaces", "spreads"]
        },
        {
            "id"          : "Q045",
            "disease"     : "Common Cold",
            "category"    : "emergency",
            "query"       : "When should cold symptoms concern me?",
            "source_pdf"  : "11_ncbi_common_cold.pdf",
            "ground_truth": "See a doctor if symptoms last more than 10 days, fever above 39°C, severe throat pain, difficulty breathing, or ear pain develop.",
            "key_terms"   : ["10 days", "fever", "doctor", "breathing"]
        },

        # ── SKIN INFECTIONS (5 questions) ────────────────────────
        {
            "id"          : "Q046",
            "disease"     : "Skin Infections",
            "category"    : "symptoms",
            "query"       : "What are signs of skin infection?",
            "source_pdf"  : "12_ncbi_skin_infections.pdf",
            "ground_truth": "Skin infection signs include redness, swelling, warmth, pain, pus or discharge, and sometimes fever. Cellulitis shows spreading redness and warmth.",
            "key_terms"   : ["redness", "swelling", "pus", "warmth"]
        },
        {
            "id"          : "Q047",
            "disease"     : "Skin Infections",
            "category"    : "treatment",
            "query"       : "How are skin infections treated?",
            "source_pdf"  : "12_ncbi_skin_infections.pdf",
            "ground_truth": "Skin infections are treated with topical or oral antibiotics depending on severity. Keep the area clean and dry. Abscesses may need draining by a doctor.",
            "key_terms"   : ["antibiotics", "clean", "topical", "treatment"]
        },
        {
            "id"          : "Q048",
            "disease"     : "Skin Infections",
            "category"    : "prevention",
            "query"       : "How to prevent skin infections?",
            "source_pdf"  : "12_ncbi_skin_infections.pdf",
            "ground_truth": "Prevent skin infections by keeping skin clean and dry, treating cuts and wounds promptly, avoiding sharing personal items, and maintaining good hygiene.",
            "key_terms"   : ["clean", "hygiene", "wounds", "prevention"]
        },
        {
            "id"          : "Q049",
            "disease"     : "Skin Infections",
            "category"    : "transmission",
            "query"       : "How do skin infections spread?",
            "source_pdf"  : "12_ncbi_skin_infections.pdf",
            "ground_truth": "Skin infections spread through direct skin contact, sharing contaminated items, and breaks in the skin. Fungal infections spread in warm moist environments.",
            "key_terms"   : ["contact", "contaminated", "spread", "fungal"]
        },
        {
            "id"          : "Q050",
            "disease"     : "Skin Infections",
            "category"    : "emergency",
            "query"       : "When is a skin infection serious?",
            "source_pdf"  : "12_ncbi_skin_infections.pdf",
            "ground_truth": "A skin infection is serious when it spreads rapidly, causes high fever, red streaks appear from the wound, or the patient feels very unwell. Go to hospital immediately.",
            "key_terms"   : ["spreads", "fever", "hospital", "emergency"]
        },
    ],

    # ── TRIAGE TEST CASES (20 emergency queries) ────────────────
    "triage_tests": [

        # Hindi RED (5)
        {"id": "T001", "lang": "hi", "query": "सीने में दर्द है और सांस नहीं आ रही", "expected": "red"},
        {"id": "T002", "lang": "hi", "query": "बेहोश हो गया है",                      "expected": "red"},
        {"id": "T003", "lang": "hi", "query": "दौरा पड़ा है",                          "expected": "red"},
        {"id": "T004", "lang": "hi", "query": "बहुत तेज बुखार और खून नहीं रुक रहा",   "expected": "red"},
        {"id": "T005", "lang": "hi", "query": "लकवा मार गया अचानक",                   "expected": "red"},

        # Tamil RED (5)
        {"id": "T006", "lang": "ta", "query": "மார்பு வலி மிகவும் கடுமையாக உள்ளது", "expected": "red"},
        {"id": "T007", "lang": "ta", "query": "மூச்சு திணறல் இருக்கிறது",            "expected": "red"},
        {"id": "T008", "lang": "ta", "query": "நினைவு இழந்தார்",                      "expected": "red"},
        {"id": "T009", "lang": "ta", "query": "வலிப்பு வந்தது",                       "expected": "red"},
        {"id": "T010", "lang": "ta", "query": "இரத்தம் நிற்கவில்லை",                 "expected": "red"},

        # Telugu RED (5)
        {"id": "T011", "lang": "te", "query": "ఛాతీ నొప్పి చాలా ఎక్కువగా ఉంది",    "expected": "red"},
        {"id": "T012", "lang": "te", "query": "శ్వాస తీసుకోలేను",                    "expected": "red"},
        {"id": "T013", "lang": "te", "query": "స్పృహ కోల్పోయాను",                    "expected": "red"},
        {"id": "T014", "lang": "te", "query": "మూర్ఛ వచ్చింది",                      "expected": "red"},
        {"id": "T015", "lang": "te", "query": "రక్తం ఆగడం లేదు",                     "expected": "red"},

        # Kannada RED (5)
        {"id": "T016", "lang": "kn", "query": "ಎದೆ ನೋವು ತುಂಬಾ ಜಾಸ್ತಿ ಇದೆ",        "expected": "red"},
        {"id": "T017", "lang": "kn", "query": "ಉಸಿರಾಡಲು ಕಷ್ಟ ಆಗುತ್ತಿದೆ",           "expected": "red"},
        {"id": "T018", "lang": "kn", "query": "ಎಚ್ಚರ ತಪ್ಪಿದೆ",                      "expected": "red"},
        {"id": "T019", "lang": "kn", "query": "ರಕ್ತ ನಿಲ್ಲುತ್ತಿಲ್ಲ",                "expected": "red"},
        {"id": "T020", "lang": "kn", "query": "ತೀವ್ರ ಜ್ವರ ಮತ್ತು ಮೂರ್ಛೆ",           "expected": "red"},
    ]
}

# Save to logs
os.makedirs("logs", exist_ok=True)
with open("logs/evaluation_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Dataset saved to logs/evaluation_dataset.json")
print(f"Queries   : {len(dataset['queries'])}")
print(f"Triage    : {len(dataset['triage_tests'])}")
print(f"Diseases  : {dataset['metadata']['diseases']}")