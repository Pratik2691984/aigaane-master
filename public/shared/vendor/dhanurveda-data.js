/* ═══════════════════════════════════════════════════════════════════════════
   Dhanurveda Studio — Data
   ═══════════════════════════════════════════════════════════════════════════
   - Catur-aṅginī: 4 classical army divisions
   - Āyudha: 20 weapons (astras + śastras)
   - Vyūha: 10 battle formations
   - 12 classical verses
   Source basis: Agni Purāṇa (ch. 249–252), Vasiṣṭha Dhanurveda,
                 Mahābhārata (Bhīṣma Parva, Droṇa Parva), Nītiprakāśikā
   ═══════════════════════════════════════════════════════════════════════════ */
window.DHANURVEDA_DATA = {

  /* ═══════════════════════════════════════════════════════════════════════
     CATUR-AṄGINĪ — Four-fold army
     ═══════════════════════════════════════════════════════════════════════ */
  caturAngini: [
    {
      id: 'ratha',
      name: 'Ratha', dev: 'रथ', iast: 'Ratha', en: 'Chariot',
      color: '#c9a04c',
      role: 'Mobile command platforms and missile artillery',
      terrain: 'Level plains, hard ground, dry battlefields',
      strengths: [
        'Devastating missile volleys from a stable platform',
        'High speed across open terrain',
        'Protected platform for elite mahārathis'
      ],
      weaknesses: [
        'Immobilized in mud, broken terrain, or thick forests',
        'Vulnerable to concentrated elephant charges',
        'Wheels and axles breakable by infantry swarms'
      ],
      weapons: ['Gāṇḍīva / composite bows', 'Nārāca and vatsadanta arrows', 'Cakras (discus)', 'Swords for close defense'],
      counters: ['Gaja (elephants crush wheels)', 'Broken or marshy terrain', 'Deep spear walls'],
      source: 'Agni Purāṇa ch. 250'
    },
    {
      id: 'gaja',
      name: 'Gaja', dev: 'गज', iast: 'Gaja', en: 'War Elephant',
      color: '#8a9bb0',
      role: 'Living siege engines and line breakers',
      terrain: 'Jungles, rough ground, dry plains',
      strengths: [
        'Smashes enemy formations and chariot wheels',
        'Elevated platform for archers and spearmen',
        'Fear-inducing presence against horses and foot soldiers'
      ],
      weaknesses: [
        'Susceptible to fire weapons and panic',
        'Vulnerable to foot soldiers targeting footpads or trunk',
        'Can stampede through friendly lines if maddened'
      ],
      weapons: ['Iron tusks (armor)', 'Ankuśa (goad)', 'Heavy spears', 'Mounted archers'],
      counters: ['Ratha (ranged anti-elephant volleys)', 'Fire arrows', 'Sound-terror tactics'],
      source: 'Agni Purāṇa ch. 251'
    },
    {
      id: 'ashva',
      name: 'Aśva', dev: 'अश्व', iast: 'Aśva', en: 'Cavalry',
      color: '#a04430',
      role: 'Scouting, pursuit, flank attacks, and harassment',
      terrain: 'Open fields, rolling hills, dry riverbeds',
      strengths: [
        'Unmatched tactical speed and repositioning',
        'Devastating flank charges against disorganized infantry',
        'Essential for pursuing routed armies'
      ],
      weaknesses: [
        'Vulnerable to pikes, caltrops, and entrenched infantry',
        'Cannot hold ground against heavy siege or elephant wedges'
      ],
      weapons: ['Prāsa (lance)', 'Asi (sabre)', 'Short composite bows'],
      counters: ['Padāti (deep spear walls)', 'Caltrops and obstacles'],
      source: 'Agni Purāṇa ch. 250'
    },
    {
      id: 'padati',
      name: 'Padāti', dev: 'पदाति', iast: 'Padāti', en: 'Infantry',
      color: '#8a96a6',
      role: 'Holders of ground, escort, siege, and close combat',
      terrain: 'All terrains, particularly fortifications, hills, forests',
      strengths: [
        'Versatile adaptability across every terrain',
        'Dense formations can halt cavalry and elephant charges',
        'Essential for capturing and holding territory'
      ],
      weaknesses: [
        'Low speed compared to mounted units',
        'Vulnerable to ranged chariot fire in open terrain'
      ],
      weapons: ['Dhanus (long bow)', 'Khaḍga (sword)', 'Carma (shield)', 'Śūla and Śakti (spears)'],
      counters: ['Ratha (ranged devastation)', 'Gaja (trampling power)'],
      source: 'Agni Purāṇa ch. 249'
    }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     ĀYUDHA — Weapons compendium (20 items)
     ═══════════════════════════════════════════════════════════════════════ */
  weapons: [
    // ── Astras (missile weapons invoked by mantra) ──
    { id: 'brahmastra', name: 'Brahmāstra', dev: 'ब्रह्मास्त्र', iast: 'Brahmāstra',
      type: 'astra', wielder: 'Brahmā · Arjuna · Rāma · Droṇa',
      nature: 'Celestial missile invoked by sacred mantra',
      effect: 'Multi-directional fire, scorches armies, neutralizes enemy astras, causes seismic upheaval.',
      counter: 'Another Brahmāstra, or absolute spiritual restraint.',
      source: 'Mahābhārata (Droṇa Parva)' },

    { id: 'pashupatastra', name: 'Pāśupatāstra', dev: 'पाशुपतास्त्र', iast: 'Pāśupatāstra',
      type: 'astra', wielder: 'Śiva · Arjuna',
      nature: 'Ultimate destructive energy weapon granted by Śiva',
      effect: 'Capable of destroying creation; summons spectral goblins, serpents, and fire spirits that consume all targets.',
      counter: 'None — must never be discharged against lesser foes.',
      source: 'Mahābhārata (Vana Parva)' },

    { id: 'narayanastra', name: 'Nārāyaṇāstra', dev: 'नारायणास्त्र', iast: 'Nārāyaṇāstra',
      type: 'astra', wielder: 'Nārāyaṇa · Aśvatthāmā',
      nature: 'Millions of fiery projectiles raining simultaneously',
      effect: 'Grows exponentially more destructive if resistance is offered.',
      counter: 'Immediate disarmament, dropping all weapons, and prostration.',
      source: 'Mahābhārata (Droṇa Parva)' },

    { id: 'agneyastra', name: 'Āgneyāstra', dev: 'आग्नेयास्त्र', iast: 'Āgneyāstra',
      type: 'astra', wielder: 'Agni · Arjuna · Droṇa',
      nature: 'Fire-manifesting projectile',
      effect: 'Engulfs target zone in unquenchable flames that burn through standard defenses.',
      counter: 'Varuṇāstra (water missile)',
      source: 'Mahābhārata · Agni Purāṇa' },

    { id: 'varunastra', name: 'Varuṇāstra', dev: 'वरुणास्त्र', iast: 'Varuṇāstra',
      type: 'astra', wielder: 'Varuṇa · Bhīṣma · Arjuna',
      nature: 'Water-manifesting projectile',
      effect: 'Summons torrents, waves, and downpours capable of extinguishing fires and drowning formations.',
      counter: 'Vāyavyāstra or Āgneyāstra',
      source: 'Mahābhārata' },

    { id: 'vayavyastra', name: 'Vāyavyāstra', dev: 'वायव्यास्त्र', iast: 'Vāyavyāstra',
      type: 'astra', wielder: 'Vāyu · Hanumān · Arjuna',
      nature: 'Wind-manifesting projectile',
      effect: 'Generates hurricane-force winds capable of lifting armies and scattering chariot divisions.',
      counter: 'Paryantāstra or mountain-anchor mantras',
      source: 'Mahābhārata' },

    { id: 'nagastra', name: 'Nāgāstra', dev: 'नागास्त्र', iast: 'Nāgāstra',
      type: 'astra', wielder: 'Arjuna · Karṇa · Aśvatthāmā',
      nature: 'Serpent-summoning missile',
      effect: 'Releases a swarm of celestial serpents that bind and constrict targets; can only be countered by specific serpent-counter astras.',
      counter: 'Garuḍāstra (eagle missile)',
      source: 'Mahābhārata (Droṇa Parva)' },

    { id: 'garudastra', name: 'Garuḍāstra', dev: 'गरुडास्त्र', iast: 'Garuḍāstra',
      type: 'astra', wielder: 'Viṣṇu · Kṛṣṇa · Arjuna',
      nature: 'Eagle-manifesting missile',
      effect: 'Summons Garuḍa and a flight of celestial eagles that devour serpents and dispel Nāgāstra.',
      counter: 'Brahmāstra',
      source: 'Mahābhārata' },

    { id: 'vayavyastra_arrow', name: 'Vāyavyāstra (Arrow Form)', dev: 'वायव्यास्त्र (बाण)', iast: 'Vāyavyāstra (bāṇa)',
      type: 'astra', wielder: 'Arjuna',
      nature: 'Wind-arrow — a variant arrow shaft form',
      effect: 'Releases compressed air pressure along the arrow\'s line of flight, cutting through structures.',
      counter: 'Brahmāstra or equivalent',
      source: 'Mahābhārata' },

    { id: 'suryastra', name: 'Sūryāstra', dev: 'सूर्यास्त्र', iast: 'Sūryāstra',
      type: 'astra', wielder: 'Sūrya · Karṇa',
      nature: 'Solar missile',
      effect: 'Unleashes concentrated blinding solar energy — scorches, blinds, and disorients.',
      counter: 'Candrāstra or blinding counter-mantra',
      source: 'Mahābhārata · Agni Purāṇa' },

    { id: 'candrastra', name: 'Candrāstra', dev: 'चन्द्रास्त्र', iast: 'Candrāstra',
      type: 'astra', wielder: 'Candra · Arjuna',
      nature: 'Lunar missile',
      effect: 'Summons cold moonlight — cools fire, calms panic, and counters solar heat.',
      counter: 'Sūryāstra',
      source: 'Agni Purāṇa' },

    // ── Śastras (hand-held weapons) ──
    { id: 'gandiva', name: 'Gāṇḍīva', dev: 'गाण्डीव', iast: 'Gāṇḍīva',
      type: 'shastra', wielder: 'Arjuna',
      nature: 'Divine celestial bow created by Brahmā',
      effect: 'Unbreakable string, golden lustre, thundering sound that strikes terror in enemies.',
      counter: 'None (wielded by the supreme archer)',
      source: 'Mahābhārata (Ādi Parva)' },

    { id: 'vijaya', name: 'Vijaya', dev: 'विजय', iast: 'Vijaya',
      type: 'shastra', wielder: 'Karṇa · Indra',
      nature: 'Celestial bow gifted by Paraśurāma to Karṇa',
      effect: 'A bow of victory, capable of firing any astra and striking down divine opponents.',
      counter: 'Gāṇḍīva',
      source: 'Mahābhārata (Karṇa Parva)' },

    { id: 'sudarshana', name: 'Sudarśana Cakra', dev: 'सुदर्शन चक्र', iast: 'Sudarśana Cakra',
      type: 'shastra', wielder: 'Viṣṇu · Kṛṣṇa',
      nature: 'Spinning serrated disc with 108 edges',
      effect: 'Returns automatically to the wielder; cleaves through armies and celestial barriers.',
      counter: 'Divine intervention or supreme illusion',
      source: 'Mahābhārata · Purāṇas' },

    { id: 'trishula', name: 'Triśūla', dev: 'त्रिशूल', iast: 'Triśūla',
      type: 'shastra', wielder: 'Śiva · Durgā',
      nature: 'Three-pronged divine trident',
      effect: 'Symbolizes mastery over past, present, and future; pierces mortal and immortal armor alike.',
      counter: 'Divine shields',
      source: 'Purāṇas' },

    { id: 'parashu', name: 'Paraśu', dev: 'परशु', iast: 'Paraśu',
      type: 'shastra', wielder: 'Paraśurāma · Śiva',
      nature: 'Battle-axe of the warrior-sage Paraśurāma',
      effect: 'Cuts through any material; symbol of Brahminical martial rage.',
      counter: 'Equivalent divine weapon',
      source: 'Mahābhārata · Purāṇas' },

    { id: 'nandaka', name: 'Nandaka', dev: 'नन्दक', iast: 'Nandaka',
      type: 'shastra', wielder: 'Viṣṇu · Kṛṣṇa',
      nature: 'Celestial sword of pure knowledge',
      effect: 'Grants unmatched close-quarters efficacy; cuts through mental and physical delusion.',
      counter: 'Parry with equivalent divine blade',
      source: 'Mahābhārata' },

    { id: 'khadga', name: 'Khaḍga', dev: 'खड्ग', iast: 'Khaḍga',
      type: 'shastra', wielder: 'All warriors',
      nature: 'Standard straight sword',
      effect: 'Primary close-quarters weapon; used after the bow is broken or discarded.',
      counter: 'Shield and parry',
      source: 'Agni Purāṇa' },

    { id: 'katar', name: 'Kaṭāri', dev: 'कटारि', iast: 'Kaṭāri',
      type: 'shastra', wielder: 'Infantry · Assassins',
      nature: 'Short punch-dagger for close combat',
      effect: 'Concealed weapon for grappling range; pierces chainmail.',
      counter: 'Shield wall',
      source: 'Nītiprakāśikā' },

    { id: 'chakra', name: 'Cakra', dev: 'चक्र', iast: 'Cakra',
      type: 'shastra', wielder: 'Viṣṇu · Kṛṣṇa · Arjuna',
      nature: 'Thrown war-disc',
      effect: 'Razor-edged discus thrown at range; returns to skilled wielder.',
      counter: 'Sudarśana Cakra or divine shield',
      source: 'Mahābhārata · Agni Purāṇa' }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     VYŪHA — 10 battle formations
     ═══════════════════════════════════════════════════════════════════════ */
  vyuhas: [
    { id: 'krauncha', name: 'Krauñca', dev: 'क्रौञ्च', iast: 'Krauñca',
      shape: 'Heron / Crane',
      deployer: 'Drupada', side: 'Pāṇḍava',
      purpose: 'Extended scouting and envelopment formation',
      counterVyuhas: ['Śyena Vyūha'],
      description: 'Formed with a sharp long beak and broad wings, designed to encircle and flank enemy defensive lines.' },

    { id: 'makara', name: 'Makara', dev: 'मकर', iast: 'Makara',
      shape: 'Crocodile',
      deployer: 'Bhīṣma', side: 'Kaurava',
      purpose: 'Impenetrable defensive holding formation',
      counterVyuhas: ['Vajra Vyūha'],
      description: 'Wide open jaws swallow advancing enemy units, while the massive body closes around trapped forces.' },

    { id: 'kurma', name: 'Kūrma', dev: 'कूर्म', iast: 'Kūrma',
      shape: 'Tortoise',
      deployer: 'Yudhiṣṭhira', side: 'Pāṇḍava',
      purpose: 'Fully protective defensive shell',
      counterVyuhas: ['Vajra Vyūha', 'Cakra Vyūha'],
      description: 'Outer shell of shields and elephants, inner reserve protected inside the "shell". Hard to break but slow to maneuver.' },

    { id: 'cakra', name: 'Cakra', dev: 'चक्र', iast: 'Cakra',
      shape: 'Wheel / Spiral',
      deployer: 'Droṇācārya', side: 'Kaurava',
      purpose: 'Rotating encirclement overwhelming from all angles',
      counterVyuhas: ['Garuda Vyūha', 'Padma Vyūha'],
      description: 'Rotating spiral formation — outer ring attacks while inner rings rest and rotate into position, creating relentless pressure.' },

    { id: 'padma', name: 'Padma', dev: 'पद्म', iast: 'Padma',
      shape: 'Lotus Flower',
      deployer: 'Droṇācārya', side: 'Kaurava',
      purpose: 'Multi-layered defensive labyrinth to trap elite commanders',
      counterVyuhas: ['Vajra Vyūha', 'Sudarśana Vyūha'],
      description: 'Concentric rotating circles resembling blooming lotus petals. Only warriors trained in entry and exit secrets (like Abhimanyu) can penetrate deeply.' },

    { id: 'garuda', name: 'Garuḍa', dev: 'गरुड', iast: 'Garuḍa',
      shape: 'Eagle in Flight',
      deployer: 'Yudhiṣṭhira · Arjuna', side: 'Pāṇḍava',
      purpose: 'Aggressive breakthrough targeting enemy commander',
      counterVyuhas: ['Makara Vyūha'],
      description: 'Beak formed by elite spearheads (Arjuna), wings by heavy cavalry and chariots, body by elephants and infantry backing the advance.' },

    { id: 'vajra', name: 'Vajra', dev: 'वज्र', iast: 'Vajra',
      shape: 'Thunderbolt / Diamond',
      deployer: 'Indra · Pāṇḍavas', side: 'Pāṇḍava',
      purpose: 'Extreme shock-value offensive wedge',
      counterVyuhas: ['Padma Vyūha'],
      description: 'Concentrated mass at the apex with maximum density behind, shattering any static defensive wall instantly.' },

    { id: 'shyena', name: 'Śyena', dev: 'श्येन', iast: 'Śyena',
      shape: 'Hawk / Falcon',
      deployer: 'Kṛṣṇa · Arjuna', side: 'Pāṇḍava',
      purpose: 'Rapid dive attack on the enemy commander',
      counterVyuhas: ['Krauñca Vyūha'],
      description: 'Narrow, spear-pointed formation that dives deep into enemy lines to target the commander, sacrificing breadth for penetration depth.' },

    { id: 'sarvatobhadra', name: 'Sarvatobhadra', dev: 'सर्वतोभद्र', iast: 'Sarvatobhadra',
      shape: 'All-Sides Auspicious Square',
      deployer: 'Yudhiṣṭhira', side: 'Pāṇḍava',
      purpose: 'Fully balanced, defensible from all directions',
      counterVyuhas: ['Cakra Vyūha'],
      description: 'Perfect square formation with equal strength on every side — no flank exposed. Slow but nearly impossible to envelop.' },

    { id: 'shakata', name: 'Śakaṭa', dev: 'शकट', iast: 'Śakaṭa',
      shape: 'Cart / Wagon',
      deployer: 'Bhīṣma · Droṇa', side: 'Kaurava',
      purpose: 'Mobile relief column and reinforcement shuttle',
      counterVyuhas: ['Vajra Vyūha'],
      description: 'Two wings of the formation move alternately as a wheeled cart — one advances while the other retreats, enabling sustained pressure without exhaustion.' }
  ],

  /* ═══════════════════════════════════════════════════════════════════════
     VERSES — 12 classical citations
     ═══════════════════════════════════════════════════════════════════════ */
  verses: [
    { source: 'Agni Purāṇa 249.1',
      dev: 'धनुर्वेदमहं वक्ष्ये पुराणागमचोदितम् । यस्माद्देवाश्च राजानो जयमाप्नुवन्ति वै ॥',
      iast: 'dhanurvedam ahaṃ vakṣye purāṇāgama-coditam | yasmād devāś ca rājāno jayam āpnuvanti vai ||',
      translation: 'I shall expound Dhanurveda, as inspired by the Purāṇas and Āgamas, by which both gods and kings attain victory.' },

    { source: 'Agni Purāṇa 249.2',
      dev: 'चतुर्विधं बलं राज्ञां रथाश्वगजपादतम् ।',
      iast: 'catur-vidhaṃ balaṃ rājñāṃ rathāśva-gaja-pādatam |',
      translation: 'The four-fold army of kings consists of chariots, horses, elephants, and foot soldiers.' },

    { source: 'Vasiṣṭha Dhanurveda 1.1',
      dev: 'धनुर्वेदं प्रवक्ष्यामि यथावदनुपूर्वशः ।',
      iast: 'dhanurvedaṃ pravakṣyāmi yathāvad anupūrvaśaḥ |',
      translation: 'I shall now expound Dhanurveda in its complete and traditional order.' },

    { source: 'Vasiṣṭha Dhanurveda 1.4',
      dev: 'अस्त्रं मन्त्रप्रभावेण शस्त्रं बाहुबलेन तु ।',
      iast: 'astraṃ mantra-prabhāveṇa śastraṃ bāhu-balena tu |',
      translation: 'Astras are empowered by mantra resonance; śastras are wielded by physical arm strength.' },

    { source: 'Agni Purāṇa 250.12',
      dev: 'धनुषा शरसंधानं कुर्याद् विद्वान् समाहितः ।',
      iast: 'dhanuṣā śara-sandhānaṃ kuryād vidvān samāhitaḥ |',
      translation: 'The wise archer should nock the arrow upon the bow with total concentration.' },

    { source: 'Agni Purāṇa 250.15',
      dev: 'लक्ष्यं विधाय मनसा शरं मुञ्चेत् सुसंयतः ।',
      iast: 'lakṣyaṃ vidhāya manasā śaraṃ muñcet su-saṃyataḥ |',
      translation: 'Fixing the target in the mind, one should release the arrow with complete self-mastery.' },

    { source: 'Mahābhārata (Bhīṣma Parva 19.20)',
      dev: 'व्यूहेन महता राजन् यथा न व्यथते बलम् ।',
      iast: 'vyūhena mahatā rājan yathā na vyathate balam |',
      translation: 'By a great battle formation, O King, one\'s army remains unshaken.' },

    { source: 'Mahābhārata (Droṇa Parva 22.47)',
      dev: 'अस्त्राणां परमं ब्रह्मास्त्रं युधि दुर्जयम् ।',
      iast: 'astrāṇāṃ paramaṃ brahmāstraṃ yudhi durjayam |',
      translation: 'Among all astras, the Brahmāstra is supreme and unconquerable in battle.' },

    { source: 'Mahābhārata (Karṇa Parva 90.9)',
      dev: 'न हि धर्मो जयत्येको नाधर्मो जयति ध्रुवम् ।',
      iast: 'na hi dharmo jayaty eko nādharmo jayati dhruvam |',
      translation: 'Neither dharma alone nor adharma alone is assured of victory — the outcome comes from effort.' },

    { source: 'Nītiprakāśikā 1.8',
      dev: 'गजानां पालनं यत्नात् कर्तव्यं नृपसत्तमैः ।',
      iast: 'gajānāṃ pālanaṃ yatnāt kartavyaṃ nṛpa-sattamaiḥ |',
      translation: 'The best of kings should carefully nurture and train their war-elephants.' },

    { source: 'Agni Purāṇa 251.3',
      dev: 'धनुः शस्त्राणि विद्याश्च जीवितं यस्य रक्षति ।',
      iast: 'dhanuḥ śastrāṇi vidyāś ca jīvitaṃ yasya rakṣati |',
      translation: 'The bow, the weapons, and the knowledge that guard one\'s life are sacred.' },

    { source: 'Mahābhārata (Udyoga Parva 134.8)',
      dev: 'युद्धं धर्म्यं प्रकुर्वीत नाधर्म्यं जातु पार्थिवः ।',
      iast: 'yuddhaṃ dharmyaṃ prakurvīta nādharmyaṃ jātu pārthivaḥ |',
      translation: 'A king should wage only righteous warfare, never unrighteous — dharma-yuddha alone is sanctioned.' }
  ]
};