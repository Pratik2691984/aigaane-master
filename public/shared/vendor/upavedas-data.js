/* ═══════════════════════════════════════════════════════════════════════════
   Upaveda Cabinet — Data
   ═══════════════════════════════════════════════════════════════════════════
   Shared data structure for:
     - /upavedas.html (cabinet page)
     - Sanskrit tab → Studios sub-view
   Order: classical (Āyurveda · Gāndharvaveda · Sthāpatyaveda · Dhanurveda)
   ═══════════════════════════════════════════════════════════════════════════ */
window.UPAVEDAS_DATA = {

  intro: {
    title: 'Upaveda Cabinet',
    dev: 'उपवेद',
    iast: 'Upaveda',
    subtitle: 'Four classical applied sciences',
    body: 'The Upavedas are the applied sciences of the Vedic tradition — four fields that translate sacred knowledge into practical arts: medicine, music, architecture, and warfare. Each rests on a classical text and a living lineage. Each has been re-imagined here as an interactive studio.'
  },

  studios: [
    /* ─────────────────────────────────────────────────────────────────
       1. ĀYURVEDA — Medicine
       ───────────────────────────────────────────────────────────────── */
    {
      id: 'ayurveda',
      order: 1,
      name: 'Āyurveda',
      dev: 'आयुर्वेद',
      iast: 'Āyurveda',
      en: 'Medicine & Life-Science',
      accent: '#7a9a5a',
      accentHi: '#a8c890',
      tagline: 'The science of life, constitution, and daily practice',
      description:
        'Āyurveda maps the human body through three doṣas — Vāta, Pitta, and Kapha — ' +
        'and prescribes balance through diet, routine, herbs, and season. Its foundational ' +
        'text is the Caraka Saṃhitā, with Suśruta and Vāgbhaṭa completing the Bṛhat Trayī.',
      features: [
        '20-question Prakṛti assessment with ranked doṣa scoring',
        '20 classical Guṇas with rasa, foods, and herbs',
        'Dinacaryā routines for each doṣa',
        'Six tastes (rasas) and their doṣa effects'
      ],
      source: 'Caraka Saṃhitā · Suśruta Saṃhitā · Aṣṭāṅga Hṛdaya',
      link: '/ayurveda.html',
      status: 'live',
      linkLabel: 'Open Āyurveda Studio'
    },

    /* ─────────────────────────────────────────────────────────────────
       2. GĀNDHARVAVEDA — Music & Drama
       ───────────────────────────────────────────────────────────────── */
    {
      id: 'gandharvaveda',
      order: 2,
      name: 'Gāndharvaveda',
      dev: 'गान्धर्ववेद',
      iast: 'Gāndharvaveda',
      en: 'Music, Drama & Sound',
      accent: '#c9a227',
      accentHi: '#e8d5a3',
      tagline: 'Music, drama, and the science of sound',
      description:
        'Gāndharvaveda is the Upaveda of music and dramatic art, attributed to Bharata Muni ' +
        'in the Nāṭyaśāstra. It codifies rāga (melodic structure), tāla (rhythmic cycle), ' +
        'rasa (emotional essence), and the metrical science of Sanskrit verse.',
      features: [
        '23 rāgas with thaat, time, aroha, avaroha, and vadi metadata',
        '9 tālas with bols, sam, khali, and tali positions',
        'Pingal mātrā scanner with Guru/Laghu detection',
        'Live tanpura drone and AI prompt generation',
        'MIDI export for external production'
      ],
      source: 'Nāṭyaśāstra · Bharata Muni',
      link: '/gandharvaveda.html',
      status: 'live',
      linkLabel: 'Open Gāndharvaveda Studio'
    },

    /* ─────────────────────────────────────────────────────────────────
       3. STHĀPATYAVEDA — Architecture
       ───────────────────────────────────────────────────────────────── */
    {
      id: 'sthapatyaveda',
      order: 3,
      name: 'Sthāpatyaveda',
      dev: 'स्थापत्यवेद',
      iast: 'Sthāpatyaveda',
      en: 'Architecture & Sacred Geometry',
      accent: '#c9a06a',
      accentHi: '#e8c090',
      tagline: 'Architecture, sacred geometry, and the art of measurement',
      description:
        'Sthāpatyaveda is the Upaveda of architecture, sculpture, and town planning. ' +
        'Its most complete text is the Mānasāra, which lays out the Vāstu Puruṣa Maṇḍala — ' +
        'an 81-square cosmic grid that every traditional building is aligned to.',
      features: [
        '81-pada Vāstu Puruṣa Maṇḍala with three overlay modes',
        '9-direction Vāstu compass with home-facing selector',
        'Māna converter: aṅgula, hasta, daṇḍa, yojana',
        'Temple proportions across four scales',
        'Three regional styles: Nāgara, Drāviḍa, Vesara'
      ],
      source: 'Mānasāra · Māyamatam · Bṛhat Saṃhitā',
      link: '/sthapatyaveda.html',
      status: 'live',
      linkLabel: 'Open Sthāpatyaveda Studio'
    },

    /* ─────────────────────────────────────────────────────────────────
       4. DHANURVEDA — Warfare
       ───────────────────────────────────────────────────────────────── */
    {
      id: 'dhanurveda',
      order: 4,
      name: 'Dhanurveda',
      dev: 'धनुर्वेद',
      iast: 'Dhanurveda',
      en: 'Archery & Martial Science',
      accent: '#8a9bb0',
      accentHi: '#b8c8dc',
      tagline: 'Archery, martial science, and strategic warfare',
      description:
        'Dhanurveda is the Upaveda of archery and warfare, elaborated in the Agni Purāṇa, ' +
        'the Vasiṣṭha Dhanurveda, and the battle books of the Mahābhārata. It covers the ' +
        'four-fold army, celestial astras, hand-held śastras, and the geometric battle formations.',
      features: [
        'Catur-aṅginī: 4 classical army divisions with counter matrix',
        '20 weapons compendium (11 astras + 9 śastras)',
        '10 battle formations from the Mahābhārata',
        '12 classical verses from Agni Purāṇa and Vasiṣṭha Dhanurveda'
      ],
      source: 'Agni Purāṇa · Vasiṣṭha Dhanurveda · Mahābhārata',
      link: '/dhanurveda.html',
      status: 'live',
      linkLabel: 'Open Dhanurveda Studio'
    }
  ],

  /* ─── Footer links ─── */
  links: [
    { label: '← Return to Aigaane', href: '/', external: false },
    { label: 'Śāstra Taxonomy',     href: '/?tab=sastra', external: false },
    { label: 'Changelog',           href: '/?tab=changelog', external: false }
  ]
};