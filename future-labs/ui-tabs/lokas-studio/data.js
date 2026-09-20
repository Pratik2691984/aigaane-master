const profile = (sattva, rajas, tamas, noise, coupling, coherenceBias, fragmentationBias, pralayaSensitive = false) => ({
  sattva,
  rajas,
  tamas,
  noise,
  coupling,
  coherenceBias,
  fragmentationBias,
  pralayaSensitive
});

export const lokasData = [
  {
    id: "brahmaloka",
    name: "Brahmaloka / Satyaloka",
    category: "upper",
    guna: "Sattva",
    desc: "The summit of the material cosmos, associated with Brahma and truth-bearing contemplation. Its sattvic brilliance is refined, long-lived, and ordered, yet still within cosmic time.",
    scriptures: "Bhagavata Purana 2.5, 3.11, 5.20-5.23; Vishnu Purana 2.7",
    promptKey: "Brahmaloka",
    collapseProfile: profile(92, 6, 2, 0.04, 0.82, 0.94, 0.06, true)
  },
  {
    id: "tapoloka",
    name: "Tapoloka",
    category: "upper",
    guna: "Sattva",
    desc: "Realm of austerity, inner heat, and luminous restraint. Tapoloka emphasizes concentrated will, disciplined perception, and sattva sharpened through tapas.",
    scriptures: "Bhagavata Purana 2.5, 3.11; Vishnu Purana 2.7",
    promptKey: "Brahmaloka",
    collapseProfile: profile(88, 10, 2, 0.05, 0.78, 0.9, 0.08, true)
  },
  {
    id: "janaloka",
    name: "Janaloka",
    category: "upper",
    guna: "Sattva",
    desc: "World of great sages and mind-born beings. It carries a contemplative sattva that preserves wisdom patterns across cycles of creation.",
    scriptures: "Bhagavata Purana 2.5, 3.11; Vishnu Purana 2.7",
    promptKey: "Brahmaloka",
    collapseProfile: profile(84, 12, 4, 0.06, 0.74, 0.87, 0.1, true)
  },
  {
    id: "maharloka",
    name: "Maharloka",
    category: "upper",
    guna: "Sattva",
    desc: "A transitional high realm of seers who perceive cosmic dissolution from above the human field. Its guna tone is sattvic, with boundary awareness between worlds.",
    scriptures: "Bhagavata Purana 2.5, 3.11; Vishnu Purana 2.7",
    promptKey: "Brahmaloka",
    collapseProfile: profile(78, 16, 6, 0.08, 0.7, 0.82, 0.13, true)
  },
  {
    id: "dhruvaloka",
    name: "Dhruvaloka",
    category: "boundary",
    guna: "Sattva",
    desc: "The fixed polar station of Dhruva, an axis of devotion and cosmic orientation. It functions as a stabilizing boundary between motion and stillness.",
    scriptures: "Bhagavata Purana 4.12, 5.23; Vishnu Purana 2.12",
    promptKey: "Dhruvaloka",
    collapseProfile: profile(86, 8, 6, 0.03, 0.9, 0.96, 0.04, false)
  },
  {
    id: "svarloka",
    name: "Svarloka",
    category: "upper",
    guna: "Rajas",
    desc: "The heavenly region of devas, sacrifice, merit, music, and radiant enjoyment. Its rajas is elevated and ceremonially ordered, not grossly turbulent.",
    scriptures: "Bhagavata Purana 5.16-5.22; Bhagavad Gita 9.20-9.21",
    promptKey: "Svarloka",
    collapseProfile: profile(46, 48, 6, 0.14, 0.68, 0.7, 0.2, false)
  },
  {
    id: "bhuvarloka",
    name: "Bhuvarloka",
    category: "middle",
    guna: "Mixed",
    desc: "The subtle atmospheric middle field of prana, ancestors, spirits, mantra currents, and liminal forces between earth and heaven.",
    scriptures: "Bhagavata Purana 2.5, 5.20-5.22; Vishnu Purana 2.7",
    promptKey: "Bhuloka",
    collapseProfile: profile(36, 44, 20, 0.22, 0.56, 0.55, 0.34, false)
  },
  {
    id: "bhuloka",
    name: "Bhuloka",
    category: "middle",
    guna: "Mixed",
    desc: "The earthly plane where karma becomes embodied, choices become visible, and all three gunas interweave through human action.",
    scriptures: "Bhagavata Purana 5.16-5.19; Bhagavad Gita 14",
    promptKey: "Bhuloka",
    collapseProfile: profile(32, 42, 26, 0.28, 0.5, 0.48, 0.42, false)
  },
  {
    id: "atala",
    name: "Atala",
    category: "lower",
    guna: "Tamas",
    desc: "A lower realm associated with enchantment, appetite, and power used for sensory domination. Its tamas is veiled by glamour.",
    scriptures: "Bhagavata Purana 5.24",
    promptKey: "Patala",
    collapseProfile: profile(12, 38, 50, 0.42, 0.45, 0.28, 0.62, false)
  },
  {
    id: "vitala",
    name: "Vitala",
    category: "lower",
    guna: "Tamas",
    desc: "A subterranean region marked by occult metallurgy, fire below the surface, and desire mixed with hidden force.",
    scriptures: "Bhagavata Purana 5.24",
    promptKey: "Patala",
    collapseProfile: profile(10, 36, 54, 0.46, 0.43, 0.25, 0.66, false)
  },
  {
    id: "sutala",
    name: "Sutala",
    category: "lower",
    guna: "Mixed",
    desc: "The realm of Bali Maharaja, lower in cosmography yet sanctified by humility and Vishnu's protection. It is a mixed realm where devotion transforms status.",
    scriptures: "Bhagavata Purana 5.24, 8.22",
    promptKey: "Sutala",
    collapseProfile: profile(48, 24, 28, 0.18, 0.7, 0.72, 0.24, false)
  },
  {
    id: "talatala",
    name: "Talatala",
    category: "lower",
    guna: "Tamas",
    desc: "The domain of Maya Danava, rich in technical illusion and architected concealment. Its tamas appears as dazzling construction and control.",
    scriptures: "Bhagavata Purana 5.24",
    promptKey: "Patala",
    collapseProfile: profile(8, 42, 50, 0.5, 0.52, 0.24, 0.68, false)
  },
  {
    id: "mahatala",
    name: "Mahatala",
    category: "lower",
    guna: "Tamas",
    desc: "A realm of serpent clans, instinctive intelligence, guarded fear, and coiled subterranean vitality.",
    scriptures: "Bhagavata Purana 5.24",
    promptKey: "Patala",
    collapseProfile: profile(7, 28, 65, 0.58, 0.38, 0.2, 0.76, false)
  },
  {
    id: "rasatala",
    name: "Rasatala",
    category: "lower",
    guna: "Tamas",
    desc: "A dense realm of daityas and danavas, shaped by rivalry, subterranean luxury, and resistance to deva order.",
    scriptures: "Bhagavata Purana 5.24",
    promptKey: "Patala",
    collapseProfile: profile(6, 34, 60, 0.56, 0.42, 0.18, 0.78, false)
  },
  {
    id: "patala",
    name: "Patala",
    category: "lower",
    guna: "Tamas",
    desc: "The deepest lower loka, beautiful and jeweled yet heavily tamasic, associated with naga sovereignty, hidden wealth, and inward-descending consciousness.",
    scriptures: "Bhagavata Purana 5.24; Vishnu Purana 2.5",
    promptKey: "Patala",
    collapseProfile: profile(5, 25, 70, 0.64, 0.34, 0.16, 0.84, false)
  }
];

export const narakasData = [
  { id: 1, name: "Tamisra", cause: "Deceiving others and taking wealth, spouse, or trust.", consequence: "Dark restraint, hunger, and disorientation mirror stolen agency.", category: "deceit", guna: "Tamas" },
  { id: 2, name: "Andhatamisra", cause: "Betrayal within intimate bonds and denial of rightful shelter.", consequence: "Blind confusion and loss of support mirror broken trust.", category: "betrayal", guna: "Tamas" },
  { id: 3, name: "Raurava", cause: "Cruelty toward beings who depended on restraint.", consequence: "Fearful pursuit returns the suffering one caused.", category: "violence", guna: "Tamas" },
  { id: 4, name: "Maharaurava", cause: "Sustained exploitation of living beings for selfish pleasure.", consequence: "Magnified terror reflects life-force consumed by exploitation.", category: "violence", guna: "Tamas" },
  { id: 5, name: "Kumbhipaka", cause: "Killing beings for indulgence while ignoring their pain.", consequence: "Boiling pressure reflects lives cooked and consumed.", category: "harm", guna: "Tamas" },
  { id: 6, name: "Kalasutra", cause: "Hostility toward the wise, sacred, parents, or protectors.", consequence: "Burning time and heat dissolve reverence turned hostile.", category: "irreverence", guna: "Tamas" },
  { id: 7, name: "Asipatravana", cause: "Rejecting dharma after knowing it or misleading others.", consequence: "Blade-like leaves cut through false doctrine and moral rebellion.", category: "adharma", guna: "Tamas" },
  { id: 8, name: "Sukaramukha", cause: "Abusing authority or punishing the innocent.", consequence: "Crushing force breaks the pride of unjust rule.", category: "injustice", guna: "Tamas" },
  { id: 9, name: "Andhakupa", cause: "Neglecting guests, dependents, animals, and vulnerable beings.", consequence: "A dark well of hostile life mirrors withheld care.", category: "neglect", guna: "Tamas" },
  { id: 10, name: "Krimibhojana", cause: "Hoarding food or wealth without offering or sharing.", consequence: "A worm-like field reflects appetite without generosity.", category: "greed", guna: "Tamas" },
  { id: 11, name: "Sandamsa", cause: "Stealing sacred property or exploiting offerings.", consequence: "Tearing instruments expose desecrated trust.", category: "sacrilege", guna: "Tamas" },
  { id: 12, name: "Taptasurmi", cause: "Sexual coercion, exploitation, or vow-breaking desire.", consequence: "Burning contact reveals desire without dharma.", category: "exploitation", guna: "Tamas" },
  { id: 13, name: "Vajrakantaka-salmali", cause: "Degrading sexuality or betraying trust through aggression.", consequence: "Thunderbolt thorns turn grasping pleasure into pain.", category: "exploitation", guna: "Tamas" },
  { id: 14, name: "Vaitarani", cause: "Leaders or householders violating duty and protection.", consequence: "A terrible river strips away false dignity and status.", category: "misrule", guna: "Tamas" },
  { id: 15, name: "Puyoda", cause: "Reducing life to impurity and degraded conduct.", consequence: "Foul immersion makes inner pollution unavoidable.", category: "impurity", guna: "Tamas" },
  { id: 16, name: "Pranarodha", cause: "Killing or tormenting creatures for sport or vanity.", consequence: "Obstructed breath returns as fear and interrupted vitality.", category: "harm", guna: "Tamas" },
  { id: 17, name: "Visasana", cause: "Using public virtue or sacrifice as a mask for cruelty.", consequence: "Exposure strips away prestige built on violence.", category: "hypocrisy", guna: "Tamas" },
  { id: 18, name: "Lalabhaksa", cause: "Sexual degradation and forced gratification.", consequence: "Vile consumption mirrors appetite without reverence.", category: "exploitation", guna: "Tamas" },
  { id: 19, name: "Sarameyadana", cause: "Violent theft, arson, poisoning, raids, or social terror.", consequence: "Fierce pursuit reflects fear inflicted on communities.", category: "social-violence", guna: "Tamas" },
  { id: 20, name: "Avici", cause: "False testimony, fraud, and deliberate deception.", consequence: "A fall without relief mirrors speech that removed ground from others.", category: "falsehood", guna: "Tamas" },
  { id: 21, name: "Ayahpana", cause: "Breaking sacred vows through intoxication.", consequence: "Molten drink burns away intoxicated escape.", category: "intoxication", guna: "Tamas" },
  { id: 22, name: "Ksharakardama", cause: "Arrogance toward elders, teachers, or the spiritually advanced.", consequence: "Caustic mire dissolves hardened pride.", category: "pride", guna: "Tamas" },
  { id: 23, name: "Raksogana-bhojana", cause: "Human sacrifice, cannibalistic cruelty, or predatory ritual.", consequence: "Being consumed reverses the logic of violent offering.", category: "extreme-violence", guna: "Tamas" },
  { id: 24, name: "Sulaprota", cause: "Piercing, trapping, or torturing beings for sport.", consequence: "Impaling pain reveals cruelty once treated as entertainment.", category: "harm", guna: "Tamas" },
  { id: 25, name: "Dandasuka", cause: "Venomous anger, malice, threats, and hidden attacks.", consequence: "Serpentine constriction returns poisonous intent.", category: "malice", guna: "Tamas" },
  { id: 26, name: "Avata-nirodhana", cause: "Imprisoning beings in darkness or suffocating confinement.", consequence: "Blocked movement mirrors denied freedom.", category: "captivity", guna: "Tamas" },
  { id: 27, name: "Paryavartana", cause: "Receiving guests or seekers with contempt instead of welcome.", consequence: "Harsh-eyed torment reflects weaponized inhospitality.", category: "inhospitality", guna: "Tamas" },
  { id: 28, name: "Suchimukha", cause: "Miserliness, hoarding, and identifying wealth as self.", consequence: "Needle-like piercing exposes constricted possessiveness.", category: "greed", guna: "Tamas" }
];

export const aparadhasData = {
  namaAparadhas: [
    { id: 1, title: "Sadhu-ninda", note: "Criticizing or dishonoring devotees and saintly persons." },
    { id: 2, title: "Dividing the name from the Lord", note: "Treating the holy name as separate from divine presence." },
    { id: 3, title: "Guru-avajna", note: "Disobeying, neglecting, or disrespecting the spiritual teacher." },
    { id: 4, title: "Sruti-sastra-ninda", note: "Blaspheming revealed scriptures or dismissing sacred authority." },
    { id: 5, title: "Artha-vada", note: "Considering the glories of the holy name exaggerated or imaginary." },
    { id: 6, title: "Namno balad papa-buddhi", note: "Committing wrongs deliberately while relying on chanting to cancel them." },
    { id: 7, title: "Equating nama with ordinary piety", note: "Treating the holy name as equal to ritual, vows, charity, or sacrifice." },
    { id: 8, title: "Careless instruction to the faithless", note: "Giving confidential teachings on the name without care for readiness." },
    { id: 9, title: "Lack of faith in nama-mahatmya", note: "Hearing the name's greatness yet remaining inattentive or distrustful." },
    { id: 10, title: "Ego and possessiveness", note: "Maintaining material ego and ownership as ultimate while chanting." }
  ],
  sevaAparadhas: [
    "Entering the temple with shoes or unclean feet.",
    "Neglecting sacred festivals.",
    "Failing to bow before the deity.",
    "Offering worship while unclean.",
    "Bowing with one hand.",
    "Circumambulating directly before the deity.",
    "Stretching legs before the deity.",
    "Sitting carelessly before the deity.",
    "Sleeping before the deity.",
    "Eating before the deity.",
    "Speaking lies before the deity.",
    "Speaking harshly before the deity.",
    "Gossiping before the deity.",
    "Quarreling before the deity.",
    "Crying for mundane reasons before the deity.",
    "Showing anger before the deity.",
    "Punishing or favoring others before the deity.",
    "Speaking cruelly before the deity.",
    "Dressing improperly during worship.",
    "Blaspheming others before the deity.",
    "Praising others in a way that displaces worship.",
    "Using vulgar language before the deity.",
    "Passing air before the deity.",
    "Offering inferior items when better are available.",
    "Eating food not first offered.",
    "Failing to offer seasonal produce.",
    "Offering tasted or used food.",
    "Sitting with one's back to the deity.",
    "Honoring others as supreme before the deity.",
    "Failing to praise the guru properly.",
    "Praising oneself before the deity.",
    "Blaspheming sacred beings connected with worship."
  ]
};

export const promptTemplates = {
  Brahmaloka: {
    title: "Brahmaloka Contemplative Field",
    guna: "Sattva",
    prompt: "Generate a sattvic cosmic prompt for Brahmaloka / Satyaloka: luminous order, truth-bearing silence, Brahma's creative intelligence, long cycles of time, and a subtle awareness that even high creation remains within the material cosmos.",
    suggestedEngine: "sonic-mandala",
    physicsHint: "Low noise, high coherence, slow harmonic drift, pralaya sensitivity enabled for upper-world dissolution studies."
  },
  Dhruvaloka: {
    title: "Dhruvaloka Axis Stabilizer",
    guna: "Sattva",
    prompt: "Generate a Dhruvaloka profile centered on polar stillness, devotional fixity, the cosmic axis, and stable orientation for a consciousness-field simulation.",
    suggestedEngine: "nakshatra",
    physicsHint: "Very low noise, high coupling, high coherence bias, fixed-axis stability."
  },
  Svarloka: {
    title: "Svarloka Deva Resonance",
    guna: "Rajas",
    prompt: "Generate a Svarloka prompt with radiant deva atmosphere, sacrifice, merit, celestial music, refined enjoyment, and rajas disciplined by ritual order.",
    suggestedEngine: "sonic-mandala",
    physicsHint: "Medium modulation, rhythmic coupling, bright harmonic motion, controlled rajas."
  },
  Bhuloka: {
    title: "Bhuloka Karma Embodiment",
    guna: "Mixed",
    prompt: "Generate a Bhuloka prompt for embodied karma, human choice, earth-plane density, mixed gunas, ethical tension, and transformation through action.",
    suggestedEngine: "anumana",
    physicsHint: "Balanced noise and coupling, mixed coherence, visible decision pressure."
  },
  Narakas: {
    title: "Naraka Consequence Mapper",
    guna: "Tamas",
    prompt: "Generate a symbolic Naraka consequence map that treats each hell as a karmic mirror: cause, distortion of consciousness, corrective consequence, and possible learning without sensationalism.",
    suggestedEngine: "collapse-lab",
    physicsHint: "High fragmentation, high stochastic texture, dense attractor traps, no real engine routing yet."
  },
  Patala: {
    title: "Patala Subterranean Descent",
    guna: "Tamas",
    prompt: "Generate a Patala prompt with jeweled darkness, naga sovereignty, hidden wealth, beautiful tamas, subterranean depth, and consciousness descending into secrecy and power.",
    suggestedEngine: "collapse-lab",
    physicsHint: "Dense sub-bass metaphor, high tamas, low coherence, heavy drone structure."
  },
  Sutala: {
    title: "Sutala Devotional Inversion",
    guna: "Mixed",
    prompt: "Generate a Sutala prompt around Bali Maharaja, humility, Vishnu's protection, lower-world dignity, surrendered power, and the transformation of hierarchy through devotion.",
    suggestedEngine: "anumana",
    physicsHint: "Mixed guna inversion, protective coupling, moderate coherence, devotional stabilizer."
  }
};

export const gunaProfiles = {
  Sattva: {
    title: "Sattva",
    traits: [
      "Stable harmonic frequencies",
      "Low noise",
      "High coherence",
      "Slow evolving soundscape"
    ],
    base: profile(100, 0, 0, 0.06, 0.78, 0.9, 0.08, false)
  },
  Rajas: {
    title: "Rajas",
    traits: [
      "Rhythmic movement",
      "Higher modulation",
      "Medium noise",
      "Dynamic coupling"
    ],
    base: profile(0, 100, 0, 0.28, 0.62, 0.48, 0.38, false)
  },
  Tamas: {
    title: "Tamas",
    traits: [
      "Dense sub-bass",
      "Heavy drones",
      "Stochastic texture",
      "High fragmentation"
    ],
    base: profile(0, 0, 100, 0.62, 0.36, 0.18, 0.82, false)
  }
};

export const pingalaPatterns = [
  {
    id: "anustubh-basic",
    name: "Anustubh Basic",
    pattern: [0, 1, 0, 1, 0, 1, 0, 1],
    legend: "0 = Laghu, 1 = Guru",
    matras: [1, 2, 1, 2, 1, 2, 1, 2]
  }
];
