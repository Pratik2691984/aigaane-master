/* ═══════════════════════════════════════════════════════════════════════════
   Āyurveda Studio — Data
   ═══════════════════════════════════════════════════════════════════════════
   - 20-question Prakṛti assessment (6 domains, weighted 1-3)
   - 20 Guṇas (10 classical pairs) with rasa, foods, herbs
   - 3 Doṣa profiles with sub-doṣas, times, seasons, signs
   - 3 Dinacaryā routines (one per doṣa)
   Source basis: Caraka Saṃhitā, Suśruta Saṃhitā, Aṣṭāṅga Hṛdaya
   ═══════════════════════════════════════════════════════════════════════════ */
window.AYURVEDA_DATA = {

  /* ═══════════════════════════════════════════════════════════════════════
     DOṢAS — 3 profiles
     ═══════════════════════════════════════════════════════════════════════ */
  doshas: {
    vata: {
      id: 'vata',
      name: 'Vāta',
      dev: 'वात',
      iast: 'Vāta',
      en: 'Wind',
      element: 'Air + Ether (Vāyu + Ākāśa)',
      location: 'Colon, pelvis, bones, joints, skin, nervous system',
      time: '2–6 AM · 2–6 PM',
      season: 'Varṣā (monsoon)',
      color: '#7a9bb8',
      qualities: ['Dry (Rūkṣa)', 'Light (Laghu)', 'Cold (Śīta)', 'Rough (Khara)', 'Subtle (Sūkṣma)', 'Mobile (Cala)'],
      subDoshas: [
        { name: 'Prāṇa',   dev: 'प्राण',   site: 'Head, chest',           governs: 'Respiration, intake, mental activity' },
        { name: 'Udāna',   dev: 'उदान',   site: 'Chest, throat',         governs: 'Speech, exhalation, upward movement' },
        { name: 'Vyāna',   dev: 'व्यान',   site: 'Heart, circulation',    governs: 'Circulation, nerve impulses, joint movement' },
        { name: 'Samāna',  dev: 'समान',   site: 'Navel, small intestine',governs: 'Digestion, assimilation, peristalsis' },
        { name: 'Apāna',   dev: 'अपान',   site: 'Colon, lower pelvis',   governs: 'Elimination, urination, menstruation, childbirth' }
      ],
      signsBalanced: ['Alert mind', 'Quick creativity', 'Regular elimination', 'Good circulation', 'Enthusiastic energy'],
      signsAggravated: ['Anxiety, restlessness', 'Dry skin, cracking joints', 'Constipation, gas, bloating', 'Insomnia, light sleep', 'Cold hands and feet']
    },

    pitta: {
      id: 'pitta',
      name: 'Pitta',
      dev: 'पित्त',
      iast: 'Pitta',
      en: 'Bile / Fire',
      element: 'Fire + Water (Agni + Jala)',
      location: 'Small intestine, stomach, liver, spleen, sweat glands, eyes, blood',
      time: '10 AM–2 PM · 10 PM–2 AM',
      season: 'Śarad (autumn)',
      color: '#c96a3a',
      qualities: ['Hot (Uṣṇa)', 'Sharp (Tīkṣṇa)', 'Liquid (Drava)', 'Oily (Snigdha)', 'Mobile (Cala)'],
      subDoshas: [
        { name: 'Pācaka',  dev: 'पाचक',   site: 'Stomach, small intestine', governs: 'Digestion, metabolism, nutrient separation' },
        { name: 'Rañjaka', dev: 'रञ्जक',   site: 'Liver, spleen',           governs: 'Blood formation, hemoglobin, bile' },
        { name: 'Sādhaka', dev: 'साधक',   site: 'Heart',                   governs: 'Emotional drive, intellect, memory' },
        { name: 'Ālocaka', dev: 'आलोचक',   site: 'Eyes',                    governs: 'Vision, perception of form' },
        { name: 'Bhrājaka',dev: 'भ्राजक',   site: 'Skin',                    governs: 'Complexion, skin temperature, luster' }
      ],
      signsBalanced: ['Sharp intellect', 'Strong digestion', 'Courage', 'Warmth, strong immunity', 'Healthy complexion'],
      signsAggravated: ['Irritability, anger', 'Heartburn, acidity, ulcers', 'Skin rashes, acne, inflammation', 'Excess body heat, sweating', 'Critical, judgmental mind']
    },

    kapha: {
      id: 'kapha',
      name: 'Kapha',
      dev: 'कफ',
      iast: 'Kapha',
      en: 'Phlegm / Water',
      element: 'Water + Earth (Jala + Pṛthvī)',
      location: 'Chest, lungs, stomach, throat, head, lymph, joints, fat tissue',
      time: '6–10 AM · 6–10 PM',
      season: 'Vasanta (spring)',
      color: '#8fa876',
      qualities: ['Heavy (Guru)', 'Slow (Manda)', 'Cold (Śīta)', 'Oily (Snigdha)', 'Smooth (Ślakṣṇa)', 'Stable (Sthira)'],
      subDoshas: [
        { name: 'Kledaka', dev: 'क्लेदक',  site: 'Stomach',                 governs: 'Moistens food, protects gastric lining' },
        { name: 'Avalambaka', dev: 'अवलम्बक', site: 'Chest, heart, lungs',  governs: 'Supports heart and lungs, lubricates chest' },
        { name: 'Bodhaka', dev: 'बोधक',   site: 'Tongue, throat',           governs: 'Taste perception, salivation' },
        { name: 'Tarpaka', dev: 'तर्पक',   site: 'Head, brain',              governs: 'Nourishes sense organs, cerebrospinal fluid' },
        { name: 'Śleṣaka', dev: 'श्लेषक',   site: 'Joints, connective tissue', governs: 'Lubricates and stabilizes joints' }
      ],
      signsBalanced: ['Strength, stamina', 'Calm, patient nature', 'Good immunity, healthy skin', 'Sound sleep', 'Steady emotions'],
      signsAggravated: ['Lethargy, heaviness', 'Mucus, congestion, colds', 'Slow digestion, weight gain', 'Oversleeping, dull mind', 'Attachment, depression']
    }
  },

  /* ═══════════════════════════════════════════════════════════════════════
     QUIZ — 20 questions across 6 domains
     ═══════════════════════════════════════════════════════════════════════ */
  quizQuestions: [
    // ── Domain 1: Physical Frame (3 questions) ──
    { id: 'frame1', domain: 'Physical Frame',
      question: 'Which best matches your natural build?',
      options: [
        { label: 'Slim, light frame; joints and veins prominent', dosha: 'vata',  weight: 3 },
        { label: 'Medium, athletic; moderate muscle definition',  dosha: 'pitta', weight: 3 },
        { label: 'Solid, sturdy; broad shoulders or heavy bone',  dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'frame2', domain: 'Physical Frame',
      question: 'How easily do you gain or lose weight?',
      options: [
        { label: 'Hard to gain weight; loses quickly under stress', dosha: 'vata',  weight: 3 },
        { label: 'Moderate; weight stable with regular habits',     dosha: 'pitta', weight: 3 },
        { label: 'Gains easily; hard to lose even with effort',     dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'frame3', domain: 'Physical Frame',
      question: 'How would you describe your typical body temperature?',
      options: [
        { label: 'Cool, often cold hands and feet',              dosha: 'vata',  weight: 3 },
        { label: 'Warm, sometimes overheated; prefer cool rooms', dosha: 'pitta', weight: 3 },
        { label: 'Cool and moist; tolerate cold well',            dosha: 'kapha', weight: 3 }
      ]
    },

    // ── Domain 2: Skin, Hair, Nails (3 questions) ──
    { id: 'skin1', domain: 'Skin & Hair',
      question: 'Your skin texture is best described as:',
      options: [
        { label: 'Dry, thin, cool to touch, prone to cracking', dosha: 'vata',  weight: 3 },
        { label: 'Warm, oily T-zone, sensitive or acne-prone',   dosha: 'pitta', weight: 3 },
        { label: 'Thick, smooth, moist, cool or pale luster',    dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'skin2', domain: 'Skin & Hair',
      question: 'Your hair tendency is:',
      options: [
        { label: 'Dry, frizzy, brittle, prone to split ends',    dosha: 'vata',  weight: 3 },
        { label: 'Fine, soft, early graying or thinning',        dosha: 'pitta', weight: 3 },
        { label: 'Thick, oily, wavy, strong and abundant',       dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'skin3', domain: 'Skin & Hair',
      question: 'Your nails tend to be:',
      options: [
        { label: 'Thin, brittle, dry, cracking easily',         dosha: 'vata',  weight: 3 },
        { label: 'Soft, flexible, warm pink',                    dosha: 'pitta', weight: 3 },
        { label: 'Thick, strong, smooth, pale',                  dosha: 'kapha', weight: 3 }
      ]
    },

    // ── Domain 3: Digestion (4 questions) ──
    { id: 'digest1', domain: 'Digestion',
      question: 'Your appetite is best characterized as:',
      options: [
        { label: 'Irregular — sometimes ravenous, sometimes forget to eat', dosha: 'vata',  weight: 3 },
        { label: 'Strong — get irritable or shaky if meals are delayed',     dosha: 'pitta', weight: 3 },
        { label: 'Steady — can skip meals with ease; feel heavy after eating', dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'digest2', domain: 'Digestion',
      question: 'Your typical digestion after a normal meal is:',
      options: [
        { label: 'Gas, bloating, or variable — changes day to day', dosha: 'vata',  weight: 3 },
        { label: 'Fast, sometimes acidic or burning',               dosha: 'pitta', weight: 3 },
        { label: 'Slow, heavy, sleepy afterwards',                  dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'digest3', domain: 'Digestion',
      question: 'Your bowel movements tend to be:',
      options: [
        { label: 'Irregular, often constipated or dry',              dosha: 'vata',  weight: 3 },
        { label: 'Regular, sometimes loose or urgent',               dosha: 'pitta', weight: 3 },
        { label: 'Regular but slow; stools heavy or sticky',         dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'digest4', domain: 'Digestion',
      question: 'Which foods do you naturally gravitate toward?',
      options: [
        { label: 'Warm, oily, comforting foods; dislike cold',       dosha: 'vata',  weight: 3 },
        { label: 'Cool, fresh, mildly spiced; dislike heavy fried',  dosha: 'pitta', weight: 3 },
        { label: 'Warm, dry, spicy foods that "cut through" heaviness', dosha: 'kapha', weight: 3 }
      ]
    },

    // ── Domain 4: Sleep & Energy (3 questions) ──
    { id: 'sleep1', domain: 'Sleep & Energy',
      question: 'Your typical sleep pattern is:',
      options: [
        { label: 'Light, interrupted; hard to fall or stay asleep', dosha: 'vata',  weight: 3 },
        { label: 'Sound, short (5–6 hours); wake alert and driven',  dosha: 'pitta', weight: 3 },
        { label: 'Deep, heavy, prolonged (8+ hours); hard to wake',  dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'sleep2', domain: 'Sleep & Energy',
      question: 'Your energy through the day:',
      options: [
        { label: 'Bursts of energy with sudden drops; variable',    dosha: 'vata',  weight: 3 },
        { label: 'Steady and intense; focused until exhausted',      dosha: 'pitta', weight: 3 },
        { label: 'Slow to start; steady through the day once going',dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'sleep3', domain: 'Sleep & Energy',
      question: 'Your dreams tend to be:',
      options: [
        { label: 'Active, fast-moving, sometimes anxious or vivid', dosha: 'vata',  weight: 3 },
        { label: 'Focused, argumentative, intense or fiery',         dosha: 'pitta', weight: 3 },
        { label: 'Calm, slow, watery, or rarely remembered',         dosha: 'kapha', weight: 3 }
      ]
    },

    // ── Domain 5: Mental & Emotional (4 questions) ──
    { id: 'mind1', domain: 'Mind & Emotions',
      question: 'Under stress you most often become:',
      options: [
        { label: 'Anxious, scattered, worried, overwhelmed',        dosha: 'vata',  weight: 3 },
        { label: 'Irritable, critical, angry, impatient',            dosha: 'pitta', weight: 3 },
        { label: 'Withdrawn, calm but sluggish, attached',           dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'mind2', domain: 'Mind & Emotions',
      question: 'Your natural learning and memory style:',
      options: [
        { label: 'Learn quickly, forget quickly; mind flits',       dosha: 'vata',  weight: 3 },
        { label: 'Sharp, precise, driven; strong recall with focus', dosha: 'pitta', weight: 3 },
        { label: 'Slow to learn, but retain well; methodical',       dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'mind3', domain: 'Mind & Emotions',
      question: 'In relationships you tend to be:',
      options: [
        { label: 'Enthusiastic and initiating, quick to change',    dosha: 'vata',  weight: 3 },
        { label: 'Warm, passionate, expects high standards',        dosha: 'pitta', weight: 3 },
        { label: 'Loyal, patient, steady, slow to change',          dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'mind4', domain: 'Mind & Emotions',
      question: 'Your speech pattern is:',
      options: [
        { label: 'Fast, talkative, jumps between topics',            dosha: 'vata',  weight: 3 },
        { label: 'Sharp, articulate, precise, sometimes cutting',    dosha: 'pitta', weight: 3 },
        { label: 'Slow, deliberate, calm, measured',                 dosha: 'kapha', weight: 3 }
      ]
    },

    // ── Domain 6: Activity & Movement (3 questions) ──
    { id: 'activity1', domain: 'Activity',
      question: 'Your natural movement style is:',
      options: [
        { label: 'Quick, light, restless; walks fast',               dosha: 'vata',  weight: 3 },
        { label: 'Purposeful, driven, competitive',                   dosha: 'pitta', weight: 3 },
        { label: 'Slow, steady, methodical, graceful',                dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'activity2', domain: 'Activity',
      question: 'How do you respond to physical exercise?',
      options: [
        { label: 'Enjoy light movement; tire easily if pushed',      dosha: 'vata',  weight: 3 },
        { label: 'Enjoy intense activity; can push hard but overheat',dosha: 'pitta', weight: 3 },
        { label: 'Prefer to avoid; need motivation to start',        dosha: 'kapha', weight: 3 }
      ]
    },
    { id: 'activity3', domain: 'Activity',
      question: 'Your typical spending and work style:',
      options: [
        { label: 'Spontaneous, scattered; starts more than finishes', dosha: 'vata',  weight: 3 },
        { label: 'Strategic, decisive, focused; plans and executes',  dosha: 'pitta', weight: 3 },
        { label: 'Steady, saves well; slow to begin, but finishes',   dosha: 'kapha', weight: 3 }
      ]
    }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     GUṆAS — 20 classical qualities (10 pairs)
     ═══════════════════════════════════════════════════════════════════════ */
  gunas: [
    // Pair 1 — Weight
    { id: 'guru',    name: 'Guru',    dev: 'गुरु',    en: 'Heavy',    pair: 'guru-laghu',     category: 'Weight',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','amla','lavana'],
      foods: ['wheat', 'ghee', 'milk', 'dates', 'rice'],
      herbs: ['ashwagandha', 'shatavari'],
      desc: 'Creates mass, groundedness, and structure.' },
    { id: 'laghu',   name: 'Laghu',   dev: 'लघु',    en: 'Light',    pair: 'guru-laghu',     category: 'Weight',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','tikta','kashaya'],
      foods: ['mung dal', 'barley', 'honey', 'green tea'],
      herbs: ['guduchi', 'triphala'],
      desc: 'Promotes agility, reduction, and clearance.' },

    // Pair 2 — Temperature
    { id: 'shita',   name: 'Śīta',    dev: 'शीत',    en: 'Cold',     pair: 'shita-ushna',    category: 'Thermal',
      pacifies: ['pitta'], aggravates: ['vata','kapha'],
      rasa: ['tikta','kashaya','madhura'],
      foods: ['cucumber', 'coconut', 'mint', 'pomegranate'],
      herbs: ['shatavari', 'coriander', 'fennel'],
      desc: 'Cools inflammation and reduces metabolic heat.' },
    { id: 'ushna',   name: 'Uṣṇa',    dev: 'उष्ण',    en: 'Hot',      pair: 'shita-ushna',    category: 'Thermal',
      pacifies: ['vata','kapha'], aggravates: ['pitta'],
      rasa: ['katu','amla','lavana'],
      foods: ['ginger', 'chili', 'black pepper', 'garlic'],
      herbs: ['pippali', 'trikatu', 'cinnamon'],
      desc: 'Stimulates digestion, circulation, and transformation.' },

    // Pair 3 — Moisture
    { id: 'snigdha', name: 'Snigdha', dev: 'स्निग्ध',  en: 'Oily',     pair: 'snigdha-ruksha', category: 'Moisture',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','amla','lavana'],
      foods: ['ghee', 'olive oil', 'avocado', 'sesame oil'],
      herbs: ['ashwagandha', 'bala'],
      desc: 'Nourishes tissues, lubricates joints, prevents dryness.' },
    { id: 'ruksha',  name: 'Rūkṣa',   dev: 'रूक्ष',    en: 'Dry',      pair: 'snigdha-ruksha', category: 'Moisture',
      pacifies: ['kapha','pitta'], aggravates: ['vata'],
      rasa: ['katu','tikta','kashaya'],
      foods: ['chickpeas', 'barley', 'popcorn', 'dry fruits'],
      herbs: ['triphala', 'guduchi'],
      desc: 'Absorbs excess moisture, tightens tissues.' },

    // Pair 4 — Tempo
    { id: 'manda',   name: 'Manda',   dev: 'मन्द',    en: 'Slow',     pair: 'manda-tikshna',  category: 'Tempo',
      pacifies: ['pitta'], aggravates: ['kapha'],
      rasa: ['madhura','kashaya'],
      foods: ['rice', 'milk', 'banana', 'sweet potato'],
      herbs: ['shatavari', 'licorice'],
      desc: 'Calms overactivity, slows hyper-metabolism.' },
    { id: 'tikshna', name: 'Tīkṣṇa',  dev: 'तीक्ष्ण',  en: 'Sharp',    pair: 'manda-tikshna',  category: 'Tempo',
      pacifies: ['kapha'], aggravates: ['pitta'],
      rasa: ['katu','amla','lavana'],
      foods: ['mustard', 'chili', 'vinegar', 'radish'],
      herbs: ['pippali', 'chitrak'],
      desc: 'Sharpens intellect, pierces blockages, quickens metabolism.' },

    // Pair 5 — Texture
    { id: 'khara',   name: 'Khara',   dev: 'खर',     en: 'Rough',    pair: 'khara-shlakshna', category: 'Texture',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','tikta','kashaya'],
      foods: ['raw vegetables', 'chickpeas', 'rye', 'buckwheat'],
      herbs: ['triphala', 'guggulu'],
      desc: 'Scrapes channels, dries excess tissue, reduces mass.' },
    { id: 'shlakshna', name: 'Ślakṣṇa', dev: 'श्लक्ष्ण', en: 'Smooth',   pair: 'khara-shlakshna', category: 'Texture',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','amla'],
      foods: ['okra', 'ghee', 'butter', 'marshmallow root'],
      herbs: ['shatavari', 'marshmallow'],
      desc: 'Smooths tissue, soothes internal surfaces.' },

    // Pair 6 — Density
    { id: 'sandra',  name: 'Sāndra',  dev: 'सान्द्र',  en: 'Solid',    pair: 'sandra-drava',   category: 'Density',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','amla'],
      foods: ['cheese', 'butter', 'avocado', 'bone broth'],
      herbs: ['ashwagandha', 'bala'],
      desc: 'Builds tissue density, adds solidity.' },
    { id: 'drava',   name: 'Drava',   dev: 'द्रव',    en: 'Liquid',   pair: 'sandra-drava',   category: 'Density',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','tikta'],
      foods: ['soup', 'juice', 'coconut water', 'herbal tea'],
      herbs: ['guduchi', 'coriander'],
      desc: 'Liquefies, dilutes, promotes flow.' },

    // Pair 7 — Mobility
    { id: 'sthira',  name: 'Sthira',  dev: 'स्थिर',   en: 'Stable',   pair: 'sthira-sara',    category: 'Mobility',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','kashaya'],
      foods: ['root vegetables', 'rice', 'ghee', 'milk'],
      herbs: ['ashwagandha', 'shatavari'],
      desc: 'Creates stability, grounds movement, steadies mind.' },
    { id: 'sara',    name: 'Sara',    dev: 'सर',     en: 'Flowing',  pair: 'sthira-sara',    category: 'Mobility',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','amla','lavana'],
      foods: ['ginger', 'leafy greens', 'beets', 'citrus'],
      herbs: ['triphala', 'guggulu'],
      desc: 'Promotes circulation, moves stagnant fluids, opens channels.' },

    // Pair 8 — Viscosity
    { id: 'picchila', name: 'Picchila', dev: 'पिच्छिल', en: 'Slimy',    pair: 'picchila-vishada', category: 'Viscosity',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura'],
      foods: ['okra', 'marshmallow', 'flaxseed', 'seaweed'],
      herbs: ['shatavari', 'licorice'],
      desc: 'Coats and protects mucous membranes.' },
    { id: 'vishada', name: 'Viśada',  dev: 'विशद',   en: 'Clear',    pair: 'picchila-vishada', category: 'Viscosity',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','tikta','kashaya'],
      foods: ['cranberry', 'barley', 'honey', 'pomegranate'],
      herbs: ['triphala', 'guduchi'],
      desc: 'Clears channels, removes coating and stagnation.' },

    // Pair 9 — Hardness
    { id: 'kathina', name: 'Kaṭhina', dev: 'कठिन',   en: 'Hard',     pair: 'kathina-mridu',  category: 'Hardness',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['kashaya','tikta'],
      foods: ['nuts', 'seeds', 'raw vegetables', 'dried beans'],
      herbs: ['guggulu', 'triphala'],
      desc: 'Strengthens tissue, resists breakdown.' },
    { id: 'mridu',   name: 'Mṛdu',    dev: 'मृदु',    en: 'Soft',     pair: 'kathina-mridu',  category: 'Hardness',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura'],
      foods: ['rice', 'ghee', 'banana', 'cooked vegetables'],
      herbs: ['shatavari', 'ashwagandha'],
      desc: 'Softens tissue, relaxes tension, soothes rigidity.' },

    // Pair 10 — Subtlety
    { id: 'sthula',  name: 'Sthūla',  dev: 'स्थूल',   en: 'Gross',    pair: 'sthula-sukshma', category: 'Subtlety',
      pacifies: ['vata'], aggravates: ['kapha'],
      rasa: ['madhura','amla'],
      foods: ['root vegetables', 'grains', 'dairy'],
      herbs: ['ashwagandha'],
      desc: 'Builds physical bulk, adds density and weight.' },
    { id: 'sukshma', name: 'Sūkṣma',  dev: 'सूक्ष्म',  en: 'Subtle',   pair: 'sthula-sukshma', category: 'Subtlety',
      pacifies: ['kapha'], aggravates: ['vata'],
      rasa: ['katu','tikta'],
      foods: ['spices', 'herbal teas', 'honey'],
      herbs: ['brahmi', 'shankhapushpi'],
      desc: 'Penetrates deep tissues, reaches subtle channels and mind.' }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     DINACARYĀ — 3 routines (one per doṣa)
     ═══════════════════════════════════════════════════════════════════════ */
  dinacaryaRules: {
    vata: {
      wake: '6:00 AM — Rise after sunrise, slowly and warmly',
      morning: 'Warm sesame-oil abhyanga (self-massage), gentle stretching, warm water',
      breakfast: 'Warm, cooked, unctuous — oats, stewed fruit, spiced milk',
      midday: 'Lunch at noon — warm grains, root vegetables, ghee, mild spices',
      afternoon: 'Light activity, avoid overstimulation; short grounding walk',
      evening: 'Warm soup or khichdi by 6:30 PM; no raw or cold foods',
      night: 'Calming herbs (ashwagandha, brahmi); dim lights; sleep by 10:00 PM',
      oil: 'Sesame (warming)',
      diet: 'Warm, moist, oily, grounding; sweet–sour–salty tastes',
      exercise: 'Gentle yoga, tai chi, walking; avoid exhaustion',
      sleep: '10:00 PM in a warm, dark room; weighted blanket helpful',
      herbs: ['ashwagandha', 'bala', 'shatavari', 'brahmi']
    },
    pitta: {
      wake: '5:30 AM — Rise before sunrise, cool and calm',
      morning: 'Coconut or sunflower-oil massage; cooling pranayama; room-temperature water',
      breakfast: 'Cool, light — sweet fruit, yogurt, mild grains',
      midday: 'Main meal at noon — fresh, cooling, sweet–bitter–astringent',
      afternoon: 'Moderate activity; avoid midday sun; nature walk',
      evening: 'Light dinner by 6:30 PM; no alcohol, no chili, no fried',
      night: 'Moonlight walk, journaling; sleep by 10:30 PM',
      oil: 'Coconut or sunflower (cooling)',
      diet: 'Fresh, cool, mildly spiced; sweet–bitter–astringent tastes',
      exercise: 'Swimming, evening strolls, non-competitive activity',
      sleep: '10:30 PM, cool room',
      herbs: ['shatavari', 'coriander', 'fennel', 'guduchi']
    },
    kapha: {
      wake: '5:00 AM — Rise before sunrise (Brahma Muhūrta)',
      morning: 'Dry brushing or warm herbal-oil massage; vigorous pranayama; warm water with honey',
      breakfast: 'Light and warm — ginger tea, stewed apple, minimal grain',
      midday: 'Lunch at noon — warm, dry, pungent–bitter–astringent; minimize dairy',
      afternoon: 'Vigorous exercise; avoid daytime napping',
      evening: 'Early light dinner by 6:00 PM; warm, spiced, dry',
      night: 'Stimulating herbs (trikatu, guggulu); sleep by 11:00 PM',
      oil: 'Herbalized sesame or dry brushing',
      diet: 'Light, warm, pungent–bitter–astringent; minimize dairy and sweets',
      exercise: 'Vigorous cardio, running, dynamic vinyasa',
      sleep: '11:00 PM; wake promptly without lingering',
      herbs: ['trikatu', 'guggulu', 'pippali', 'punarnava']
    }
  },

  /* ═══════════════════════════════════════════════════════════════════════
     RASA — 6 tastes (used by guṇa cards and prompt generator)
     ═══════════════════════════════════════════════════════════════════════ */
  rasas: [
    { id: 'madhura', name: 'Madhura', dev: 'मधुर',   en: 'Sweet',      elements: 'Earth + Water', doshaEffect: { vata: '↓', pitta: '↓', kapha: '↑' }, examples: 'wheat, milk, dates' },
    { id: 'amla',    name: 'Amla',    dev: 'अम्ल',    en: 'Sour',       elements: 'Earth + Fire',  doshaEffect: { vata: '↓', pitta: '↑', kapha: '↑' }, examples: 'lemon, yogurt, vinegar' },
    { id: 'lavana',  name: 'Lavaṇa',  dev: 'लवण',    en: 'Salty',      elements: 'Water + Fire',  doshaEffect: { vata: '↓', pitta: '↑', kapha: '↑' }, examples: 'sea salt, seaweed' },
    { id: 'katu',    name: 'Kaṭu',    dev: 'कटु',    en: 'Pungent',    elements: 'Fire + Air',    doshaEffect: { vata: '↑', pitta: '↑', kapha: '↓' }, examples: 'ginger, chili, pepper' },
    { id: 'tikta',   name: 'Tikta',   dev: 'तिक्त',   en: 'Bitter',     elements: 'Air + Ether',   doshaEffect: { vata: '↑', pitta: '↓', kapha: '↓' }, examples: 'turmeric, neem, bitter greens' },
    { id: 'kashaya', name: 'Kaṣāya',  dev: 'कषाय',   en: 'Astringent', elements: 'Air + Earth',   doshaEffect: { vata: '↑', pitta: '↓', kapha: '↓' }, examples: 'pomegranate, chickpeas, tea' }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     VERSES — 6 classical snippets (for the About tab)
     ═══════════════════════════════════════════════════════════════════════ */
  verses: [
    { source: 'Caraka Saṃhitā 1.1.24',
      dev: 'धातुसाम्यमायुर्वेदः',
      iast: 'dhātusāmyam āyurvedaḥ',
      translation: 'Āyurveda is [the science of] maintaining the balance of the bodily elements.' },
    { source: 'Suśruta Saṃhitā 1.1.3',
      dev: 'वातपित्तकफा वायुः पित्तं श्लेष्मेति चापरे ।',
      iast: 'vātapittakaphā vāyuḥ pittaṃ śleṣmeti cāpare |',
      translation: 'Vāta, Pitta, and Kapha — also called Vāyu, Pitta, and Śleṣma.' },
    { source: 'Aṣṭāṅga Hṛdaya 1.1',
      dev: 'रागादिरोगान् सततानुषक्तानशेषकायप्रसृतानशेषान् ।',
      iast: 'rāgādi-rogān satatānuṣaktān aśeṣa-kāya-prasṛtān aśeṣān |',
      translation: 'Diseases born of desire and aversion, endlessly clinging, spreading through the whole body —' },
    { source: 'Caraka Saṃhitā 1.1.41',
      dev: 'समदोषः समाग्निश्च समधातुमलक्रियः । प्रसन्नात्मेन्द्रियमनाः स्वस्थ इत्यभिधीयते ॥',
      iast: 'sama-doṣaḥ samāgniś ca sama-dhātu-mala-kriyaḥ | prasannātmendriya-manāḥ svastha ity abhidhīyate ||',
      translation: 'One whose doṣas, agni, dhātus, and malas are balanced, and whose self, senses, and mind are joyful — is called healthy.' },
    { source: 'Caraka Saṃhitā 1.1.58',
      dev: 'अन्नं ब्रह्मेति मन्यन्ते',
      iast: 'annaṃ brahmeti manyante',
      translation: 'They consider food itself to be Brahman.' },
    { source: 'Aṣṭāṅga Hṛdaya 1.2.1',
      dev: 'आयुर्वेदः सुखायुष्यमायुर्वेदः सदा हितः ।',
      iast: 'āyurvedaḥ sukhāyuṣyam āyurvedaḥ sadā hitaḥ |',
      translation: 'Āyurveda is the Veda of life and longevity, always beneficent.' }
  ]
};