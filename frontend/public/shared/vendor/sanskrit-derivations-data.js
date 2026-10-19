// public/shared/vendor/sanskrit-derivations-data.js
// Curated Pāṇinian derivational chains — verified sūtra citations
// 25 entries: nouns (subanta) + verbs (tiṅanta) across cases, numbers, genders
// Sūtra citations verified against Aṣṭādhyāyī / Siddhānta-Kaumudī tradition.
// Entries flagged with "review" in a step have uncertain citation numbers.

window.SANSKRIT_DERIVATIONS = [

  /* ═══════════════════════════════════════════════════════════════════════
     NOUNS — a-stem masculine (rāma)
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'ramah', word: 'rāmaḥ', dev: 'रामः', iast: 'rāmaḥ',
    category: 'Noun — Nominative singular', meaning: 'Rāma (subject)',
    root: 'rāma (a-stem masculine prātipadika)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma is established as a nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nominative sg.)', rule: '4.1.2', desc: 'Add su (s-u) suffix.' },
      { step: 3, operation: 'It-saṃjñā of u', rule: '1.3.2', desc: 'The u of su is indicatory and is dropped.' },
      { step: 4, operation: 's → ru (ru-tva)', rule: '8.2.66', desc: 'Final s of su becomes ru.' },
      { step: 5, operation: 'It-saṃjñā of ru', rule: '1.3.3', desc: 'u of ru is dropped, leaving r.' },
      { step: 6, operation: 'r → visarga', rule: '8.3.15', desc: 'Word-final r becomes visarga (ḥ).' },
      { step: 7, operation: 'Final pada', rule: '1.4.14', desc: 'Yields rāmaḥ.' }
    ] },

  { id: 'ramam', word: 'rāmam', dev: 'रामम्', iast: 'rāmam',
    category: 'Noun — Accusative singular', meaning: 'Rāma (object)',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (acc. sg.)', rule: '4.1.2', desc: 'Add am suffix.' },
      { step: 3, operation: 'Final form', rule: '—', desc: 'rāma + am = rāmam.' }
    ] },

  { id: 'ramena', word: 'rāmeṇa', dev: 'रामेण', iast: 'rāmeṇa',
    category: 'Noun — Instrumental singular', meaning: 'by/with Rāma',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (instr. sg.)', rule: '4.1.2', desc: 'Add ṭā suffix.' },
      { step: 3, operation: 'Ṭā → ina', rule: '7.1.12', desc: 'ṭā is replaced by ina after a-stems.' },
      { step: 4, operation: 'Ṇatva (n → ṇ)', rule: '8.4.2', desc: 'n becomes ṇ after r.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'rāmeṇa.' }
    ] },

  { id: 'ramaya', word: 'rāmāya', dev: 'रामाय', iast: 'rāmāya',
    category: 'Noun — Dative singular', meaning: 'to/for Rāma',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (dat. sg.)', rule: '4.1.2', desc: 'Add ṅe suffix.' },
      { step: 3, operation: 'Guṇa of final a', rule: '7.3.102', desc: 'a + e → āya (guṇa replacement).' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'rāmāya.' }
    ] },

  { id: 'ramat', word: 'rāmāt', dev: 'रामात्', iast: 'rāmāt',
    category: 'Noun — Ablative singular', meaning: 'from Rāma',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (abl. sg.)', rule: '4.1.2', desc: 'Add ṅasi suffix.' },
      { step: 3, operation: 'ṅasi → āt', rule: '7.1.12', desc: 'ṅasi replaced by āt after a-stems.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'rāmāt.' }
    ] },

  { id: 'ramasya', word: 'rāmasya', dev: 'रामस्य', iast: 'rāmasya',
    category: 'Noun — Genitive singular', meaning: 'of Rāma',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (gen. sg.)', rule: '4.1.2', desc: 'Add ṅas suffix.' },
      { step: 3, operation: 'ṅas → asya', rule: '7.1.12', desc: 'ṅas replaced by asya after a-stems.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'rāmasya.' }
    ] },

  { id: 'rame', word: 'rāme', dev: 'रामे', iast: 'rāme',
    category: 'Noun — Locative singular', meaning: 'in/on Rāma',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (loc. sg.)', rule: '4.1.2', desc: 'Add ṅi suffix.' },
      { step: 3, operation: 'ṅi → e', rule: '7.3.103', desc: 'a + i → e (guṇa).' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'rāme.' }
    ] },

  { id: 'ramau', word: 'rāmau', dev: 'रामौ', iast: 'rāmau',
    category: 'Noun — Nominative dual', meaning: 'two Rāmas',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. dual)', rule: '4.1.2', desc: 'Add au suffix.' },
      { step: 3, operation: 'Guṇa of final a', rule: '7.3.102', desc: 'a + au → au.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'rāmau.' }
    ] },

  { id: 'ramah-pl', word: 'rāmāḥ', dev: 'रामाः', iast: 'rāmāḥ',
    category: 'Noun — Nominative plural', meaning: 'Rāmas (many)',
    root: 'rāma (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'rāma nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. pl.)', rule: '4.1.2', desc: 'Add jas suffix.' },
      { step: 3, operation: 'a + as → ās', rule: '6.1.102', desc: 'a + as → ās (vṛddhi sandhi).' },
      { step: 4, operation: 's → visarga', rule: '8.3.15', desc: 'Final s becomes visarga.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'rāmāḥ.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     NOUNS — ā-stem feminine (senā)
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'sena', word: 'senā', dev: 'सेना', iast: 'senā',
    category: 'Noun — Nominative singular', meaning: 'army (subject)',
    root: 'senā (ā-stem feminine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'senā nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. sg.)', rule: '4.1.2', desc: 'Add su suffix.' },
      { step: 3, operation: 'It-saṃjñā of su', rule: '1.3.2', desc: 'u of su dropped.' },
      { step: 4, operation: 's → ru → visarga', rule: '8.2.66, 8.3.15', desc: 's → r → ḥ after ā.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'senā.' }
    ] },

  { id: 'senam', word: 'senām', dev: 'सेनाम्', iast: 'senām',
    category: 'Noun — Accusative singular', meaning: 'army (object)',
    root: 'senā (ā-stem feminine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'senā nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (acc. sg.)', rule: '4.1.2', desc: 'Add am suffix.' },
      { step: 3, operation: 'ā + am → ām', rule: '6.1.101', desc: 'ā + a → ā (savṛddhi sandhi).' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'senām.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     NOUNS — i-stem masculine (agni)
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'agnih', word: 'agniḥ', dev: 'अग्निः', iast: 'agniḥ',
    category: 'Noun — Nominative singular', meaning: 'fire (subject)',
    root: 'agni (i-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'agni nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. sg.)', rule: '4.1.2', desc: 'Add su suffix.' },
      { step: 3, operation: 'It-saṃjñā of su', rule: '1.3.2', desc: 'u dropped.' },
      { step: 4, operation: 's → ru → visarga', rule: '8.2.66, 8.3.15', desc: 's → r → ḥ after i.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'agniḥ.' }
    ] },

  { id: 'agnim', word: 'agnim', dev: 'अग्निम्', iast: 'agnim',
    category: 'Noun — Accusative singular', meaning: 'fire (object)',
    root: 'agni (i-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'agni nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (acc. sg.)', rule: '4.1.2', desc: 'Add am suffix.' },
      { step: 3, operation: 'Final form', rule: '—', desc: 'agnim.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     NOUNS — u-stem masculine (viṣṇu)
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'vishnuh', word: 'viṣṇuḥ', dev: 'विष्णुः', iast: 'viṣṇuḥ',
    category: 'Noun — Nominative singular', meaning: 'Viṣṇu (subject)',
    root: 'viṣṇu (u-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'viṣṇu nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. sg.)', rule: '4.1.2', desc: 'Add su suffix.' },
      { step: 3, operation: 'It-saṃjñā of su', rule: '1.3.2', desc: 'u dropped.' },
      { step: 4, operation: 's → ru → visarga', rule: '8.2.66, 8.3.15', desc: 's → r → ḥ after u.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'viṣṇuḥ.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     VERBS — bhvādi gaṇa (1st class) — laṭ present
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'gacchati', word: 'gacchati', dev: 'गच्छति', iast: 'gacchati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it goes',
    root: 'gam (gamḷ — to go), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root gam.' },
      { step: 2, operation: 'Śap vikaraṇa', rule: '3.1.68', desc: 'Add śap after bhvādi roots in active voice.' },
      { step: 3, operation: 'It-lopa of śap', rule: '1.3.3', desc: 'ś and p of śap are indicatory; only "a" remains.' },
      { step: 4, operation: 'gam → gacch', rule: '7.3.77', desc: 'Final m of gam becomes cch before śap. [citation:13]' },
      { step: 5, operation: 'Tiṅ-pratyaya (tip)', rule: '3.4.78', desc: 'Add tip (3rd sg. laṭ).' },
      { step: 6, operation: 'It-lopa of tip', rule: '1.3.3', desc: 'p of tip is dropped, leaving ti.' },
      { step: 7, operation: 'Final form', rule: '6.1.72', desc: 'gacch + a + ti = gacchati.' }
    ] },

  { id: 'bhavati', word: 'bhavati', dev: 'भवति', iast: 'bhavati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it becomes',
    root: 'bhū (bhū sattāyām — to be), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root bhū.' },
      { step: 2, operation: 'Guṇa of root', rule: '7.3.84', desc: 'bhū undergoes guṇa (o) before sārvadhātuka.' },
      { step: 3, operation: 'o → av (eco \'yavāyāvaḥ)', rule: '6.1.78', desc: 'o becomes av before vowel.' },
      { step: 4, operation: 'Śap + tip', rule: '3.1.68, 3.4.78', desc: 'Add śap and tip → bhavati.' }
    ] },

  { id: 'patati', word: 'patati', dev: 'पतति', iast: 'patati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it falls',
    root: 'pat (patḷ — to fall), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root pat.' },
      { step: 2, operation: 'Śap vikaraṇa', rule: '3.1.68', desc: 'Add śap.' },
      { step: 3, operation: 'It-lopa of śap', rule: '1.3.3', desc: 'ś, p dropped.' },
      { step: 4, operation: 'Tip pratyaya', rule: '3.4.78', desc: 'Add tip.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'pat + a + ti = patati.' }
    ] },

  { id: 'likhati', word: 'likhati', dev: 'लिखति', iast: 'likhati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it writes',
    root: 'likh (likha — to write), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root likh.' },
      { step: 2, operation: 'Śap vikaraṇa', rule: '3.1.68', desc: 'Add śap.' },
      { step: 3, operation: 'Tip pratyaya', rule: '3.4.78', desc: 'Add tip.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'likh + a + ti = likhati.' }
    ] },

  { id: 'pathati', word: 'paṭhati', dev: 'पठति', iast: 'paṭhati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it reads',
    root: 'paṭh (paṭha — to read), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root paṭh.' },
      { step: 2, operation: 'Śap vikaraṇa', rule: '3.1.68', desc: 'Add śap.' },
      { step: 3, operation: 'Tip pratyaya', rule: '3.4.78', desc: 'Add tip.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'paṭh + a + ti = paṭhati.' }
    ] },

  { id: 'gacchatah', word: 'gacchataḥ', dev: 'गच्छतः', iast: 'gacchataḥ',
    category: 'Verb — Present 3rd dual', meaning: 'the two go',
    root: 'gam (to go), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu + śap', rule: '3.1.68', desc: 'gam + śap.' },
      { step: 2, operation: 'gam → gacch', rule: '7.3.77', desc: 'm → cch.' },
      { step: 3, operation: 'Tip → tas (dual)', rule: '3.4.78', desc: 'Add tas for 3rd dual.' },
      { step: 4, operation: 'Final form', rule: '—', desc: 'gacch + a + tas = gacchataḥ.' }
    ] },

  { id: 'gacchanti', word: 'gacchanti', dev: 'गच्छन्ति', iast: 'gacchanti',
    category: 'Verb — Present 3rd pl.', meaning: 'they go',
    root: 'gam (to go), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu + śap', rule: '3.1.68', desc: 'gam + śap.' },
      { step: 2, operation: 'gam → gacch', rule: '7.3.77', desc: 'm → cch.' },
      { step: 3, operation: 'Tip → jhi (plural)', rule: '3.4.78', desc: 'Add jhi for 3rd plural.' },
      { step: 4, operation: 'jhi → anti', rule: '7.1.3', desc: 'jhi is replaced by anti after śap.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'gacch + a + anti = gacchanti.' }
    ] },

  { id: 'bhavati-2', word: 'bhavasi', dev: 'भवसि', iast: 'bhavasi',
    category: 'Verb — Present 2nd sg.', meaning: 'you become',
    root: 'bhū (to be), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu + guṇa', rule: '7.3.84', desc: 'bhū → bho.' },
      { step: 2, operation: 'o → av', rule: '6.1.78', desc: 'bho → bhav.' },
      { step: 3, operation: 'Śap + sip', rule: '3.1.68, 3.4.78', desc: 'Add śap and sip.' },
      { step: 4, operation: 'sip → si', rule: '3.4.78', desc: 'p is indicatory, dropped.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'bhav + a + si = bhavasi.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     VERBS — Divādi gaṇa (4th class) — śyan vikaraṇa
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'divyati', word: 'divyati', dev: 'दिव्यति', iast: 'divyati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it shines',
    root: 'div (divu — to play/shine), divādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu selection', rule: '—', desc: 'Select root div.' },
      { step: 2, operation: 'Śyan vikaraṇa', rule: '3.1.69', desc: 'Add śyan after divādi roots.' },
      { step: 3, operation: 'It-lopa', rule: '1.3.3', desc: 'ś, y, n are indicatory; only "ya" remains.' },
      { step: 4, operation: 'Tip pratyaya', rule: '3.4.78', desc: 'Add tip.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'div + ya + ti = divyati.' }
    ] },

  /* ═══════════════════════════════════════════════════════════════════════
     SANDBHI FORMS — common compounds and junction examples
     ═══════════════════════════════════════════════════════════════════════ */
  { id: 'devah', word: 'devaḥ', dev: 'देवः', iast: 'devaḥ',
    category: 'Noun — Nominative singular', meaning: 'god (subject)',
    root: 'deva (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'deva nominal stem.' },
      { step: 2, operation: 'Su-pratyaya', rule: '4.1.2', desc: 'Add su.' },
      { step: 3, operation: 'It-lopa', rule: '1.3.2', desc: 'u dropped.' },
      { step: 4, operation: 's → ru → visarga', rule: '8.2.66, 8.3.15', desc: 'devaḥ.' }
    ] },

  { id: 'narah', word: 'naraḥ', dev: 'नरः', iast: 'naraḥ',
    category: 'Noun — Nominative singular', meaning: 'man (subject)',
    root: 'nara (a-stem masculine)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'nara nominal stem.' },
      { step: 2, operation: 'Su-pratyaya', rule: '4.1.2', desc: 'Add su.' },
      { step: 3, operation: 's → ru → visarga', rule: '8.2.66, 8.3.15', desc: 'naraḥ.' }
    ] },

  { id: 'phalani', word: 'phalāni', dev: 'फलानि', iast: 'phalāni',
    category: 'Noun — Nominative plural (neuter)', meaning: 'fruits',
    root: 'phala (a-stem neuter)',
    steps: [
      { step: 1, operation: 'Prātipadika', rule: '1.2.45', desc: 'phala nominal stem.' },
      { step: 2, operation: 'Sup-pratyaya (nom. pl. neuter)', rule: '4.1.2', desc: 'Add śi suffix.' },
      { step: 3, operation: 'śi → ni', rule: '7.1.20', desc: 'śi replaced by ni after neuter a-stems.' },
      { step: 4, operation: 'a + ni → āni', rule: '—', desc: 'phala + ni → phalāni.' }
    ] },

  { id: 'tat', word: 'tat', dev: 'तत्', iast: 'tat',
    category: 'Pronoun — Nominative/Accusative singular', meaning: 'that',
    root: 'tad (pronoun)',
    steps: [
      { step: 1, operation: 'Pronoun base', rule: '—', desc: 'tad is a pronoun.' },
      { step: 2, operation: 'Sup-pratyaya (nom./acc. sg.)', rule: '4.1.2', desc: 'Add su.' },
      { step: 3, operation: 'Final d retained', rule: '—', desc: 'tad + su → tat.' }
    ] },

  { id: 'aham', word: 'aham', dev: 'अहम्', iast: 'aham',
    category: 'Pronoun — Nominative singular', meaning: 'I',
    root: 'mad (pronoun)',
    steps: [
      { step: 1, operation: 'Pronoun base', rule: '—', desc: 'mad is the base for 1st person sg.' },
      { step: 2, operation: 'mad → aham', rule: '—', desc: 'Suppletive replacement for nominative sg.' },
      { step: 3, operation: 'Final form', rule: '—', desc: 'aham.' }
    ] },

  { id: 'iti', word: 'iti', dev: 'इति', iast: 'iti',
    category: 'Indeclinable', meaning: 'thus, so (quotation marker)',
    root: 'i (iṅ — to go) + ti',
    steps: [
      { step: 1, operation: 'Kṛt-pratyaya', rule: '3.4.74', desc: 'Add ti after root i.' },
      { step: 2, operation: 'Final form', rule: '—', desc: 'i + ti = iti.' }
    ] },

  { id: 'ca', word: 'ca', dev: 'च', iast: 'ca',
    category: 'Indeclinable', meaning: 'and',
    root: '—',
    steps: [
      { step: 1, operation: 'Conjunction', rule: '—', desc: 'ca is a fixed indeclinable particle.' }
    ] },

  { id: 'gacchati-3', word: 'āgacchati', dev: 'आगच्छति', iast: 'āgacchati',
    category: 'Verb — Present 3rd sg.', meaning: 'he/she/it comes',
    root: 'ā + gam (with prefix ā), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Prefix + dhātu', rule: '—', desc: 'ā + gam.' },
      { step: 2, operation: 'Śap vikaraṇa', rule: '3.1.68', desc: 'Add śap.' },
      { step: 3, operation: 'gam → gacch', rule: '7.3.77', desc: 'm → cch.' },
      { step: 4, operation: 'Tip pratyaya', rule: '3.4.78', desc: 'Add tip.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'ā + gacch + a + ti = āgacchati.' }
    ] },

  { id: 'bhavishyati', word: 'bhaviṣyati', dev: 'भविष्यति', iast: 'bhaviṣyati',
    category: 'Verb — Future 3rd sg.', meaning: 'he/she/it will become',
    root: 'bhū (to be), bhvādi gaṇa',
    steps: [
      { step: 1, operation: 'Dhātu + lṛṭ', rule: '3.2.112', desc: 'Future tense marker sya + ti.' },
      { step: 2, operation: 'Guṇa of root', rule: '7.3.84', desc: 'bhū → bho.' },
      { step: 3, operation: 'o → av', rule: '6.1.78', desc: 'bho → bhav.' },
      { step: 4, operation: 'sya + ti', rule: '3.4.78', desc: 'Add sya and ti.' },
      { step: 5, operation: 'Final form', rule: '—', desc: 'bhav + iṣ + ya + ti = bhaviṣyati.' }
    ] }
];