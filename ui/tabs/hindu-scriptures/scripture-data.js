const aigaaneLinks = {
  chandas: {
    module: "pingala",
    futureTarget: "sonic-mandala",
    note: "Can later drive Laghu/Guru rhythmic sequencing."
  },
  jyotisha: {
    module: "atma-clock",
    futureTarget: "nakshatra-engine",
    note: "Can later connect ritual timing, lunar cycles, and Nakshatra calculations."
  },
  nyaya: {
    module: "anumana",
    futureTarget: "anumana-engine",
    note: "Logical inference framework for the Anumana engine."
  },
  gandharvaveda: {
    module: "sonic",
    futureTarget: "sonic-mandala",
    note: "Musicology and rasa theory can later feed sound generation."
  },
  samaveda: {
    module: "shruti-sound",
    futureTarget: "sonic-mandala",
    note: "Melodic chant logic can later inform Shruti-based synthesis."
  },
  puranas: {
    module: "lokas-studio",
    futureTarget: "lokas-studio",
    note: "Cosmology, Lokas, Narakas, and cyclic time structures connect to Lokas Studio."
  },
  vedanta: {
    module: "invariant-boundary",
    futureTarget: "collapse-lab",
    note: "Can later map boundary-condition philosophy to Collapse Lab documentation only, not runtime math."
  }
};

const node = (id, name, type, layer, category, canonicalStatus, data = {}) => ({
  id,
  name,
  type,
  layer,
  category,
  canonicalStatus,
  ...data
});

const veda = (id, name, data) => node(id, name, "veda", "sruti", "veda", "primary", data);

export const scriptureTreeData = {
  id: "sastra-root",
  name: "📜 HINDU SCRIPTURES (Śāstra)",
  type: "root",
  layer: "root",
  category: "taxonomy",
  canonicalStatus: "root",
  essence: "A layered sacred and intellectual library preserving revelation, remembered tradition, ritual practice, philosophy, and cultural memory.",
  keywords: ["sastra", "scripture", "veda", "smriti", "sruti"],
  children: [
    node("sruti", "ŚRUTI", "top-level", "sruti", "sruti", "revealed", {
      essence: "Revealed Vedic knowledge: mantra, ritual exposition, forest teaching, and Upaniṣadic inquiry.",
      keywords: ["sruti", "veda", "revelation", "apauruseya", "mantra"],
      notes: "Śruti is traditionally treated as apauruṣeya, not authored by a human person.",
      children: [
        veda("rigveda", "Ṛgveda", {
          essence: "The oldest Vedic collection of hymns, praising deities through mantra, meter, vision, and cosmic order.",
          keywords: ["rigveda", "rk", "hymn", "mantra", "indra", "agni"],
          sakhas: ["Śākala", "Bāṣkala"],
          components: {
            samhita: "Ṛgveda Saṃhitā",
            brahmanas: ["Aitareya Brāhmaṇa", "Kauṣītaki Brāhmaṇa"],
            aranyakas: ["Aitareya Āraṇyaka", "Kauṣītaki Āraṇyaka"],
            upanishads: ["Aitareya Upaniṣad", "Kauṣītaki Upaniṣad"],
            stats: { mandalas: 10, hymns: 1028 }
          },
          notes: "Central to mantra, chandas, early cosmology, and yajña language.",
          relatedNodes: ["chandas", "shiksha", "itihasas"]
        }),
        node("yajurveda", "Yajurveda", "veda", "sruti", "veda", "primary", {
          essence: "The Veda of sacrificial formulae, coordinating mantra with ritual action.",
          keywords: ["yajurveda", "yajus", "sacrifice", "ritual", "yajna"],
          sakhas: ["Śukla Yajurveda", "Kṛṣṇa Yajurveda"],
          components: {
            samhita: "Yajurveda Saṃhitās",
            brahmanas: ["Śatapatha Brāhmaṇa", "Taittirīya Brāhmaṇa"],
            aranyakas: ["Bṛhadāraṇyaka material", "Taittirīya Āraṇyaka"],
            upanishads: ["Īśa", "Bṛhadāraṇyaka", "Taittirīya", "Kaṭha", "Śvetāśvatara", "Maitrī"],
            stats: { majorRecensionalStreams: 2 }
          },
          notes: "Preserves the Śukla / Kṛṣṇa split between clearer separation and interwoven mantra-explanation traditions.",
          relatedNodes: ["kalpa", "dharmasastras", "vedanta"],
          children: [
            veda("sukla-yajurveda", "Śukla Yajurveda", {
              essence: "The white Yajurveda, with clearer separation between mantra Saṃhitā and Brāhmaṇa exposition.",
              keywords: ["sukla yajurveda", "vajasaneyi", "satapatha", "isha", "brhadaranyaka"],
              sakhas: ["Mādhyandina", "Kāṇva"],
              components: {
                samhita: "Vājasaneyi Saṃhitā",
                brahmanas: ["Śatapatha Brāhmaṇa"],
                aranyakas: ["Bṛhadāraṇyaka material"],
                upanishads: ["Īśa Upaniṣad", "Bṛhadāraṇyaka Upaniṣad"],
                stats: { principalSakhas: 2 }
              },
              notes: "Especially important for Śatapatha ritual theology and Bṛhadāraṇyaka philosophy.",
              relatedNodes: ["vedanta", "kalpa"]
            }),
            veda("krishna-yajurveda", "Kṛṣṇa Yajurveda", {
              essence: "The black Yajurveda, where mantra and explanatory prose are more interwoven.",
              keywords: ["krishna yajurveda", "taittiriya", "katha", "maitrayani"],
              sakhas: ["Taittirīya", "Maitrāyaṇī", "Kaṭha", "Kapiṣṭhala-Kaṭha"],
              components: {
                samhita: "Taittirīya, Maitrāyaṇī, Kaṭha, and related Saṃhitās",
                brahmanas: ["Taittirīya Brāhmaṇa"],
                aranyakas: ["Taittirīya Āraṇyaka"],
                upanishads: ["Taittirīya", "Kaṭha", "Śvetāśvatara", "Maitrī"],
                stats: { principalSakhas: 4 }
              },
              notes: "A major source for ritual, phonetic, and philosophical traditions.",
              relatedNodes: ["kalpa", "vedangas"]
            })
          ]
        }),
        veda("samaveda", "Sāmaveda", {
          essence: "The Veda of chant, recasting mantra into melodic liturgical performance.",
          keywords: ["samaveda", "saman", "chant", "music", "shruti", "melody"],
          sakhas: ["Kauthuma", "Rāṇāyanīya", "Jaiminīya"],
          components: {
            samhita: "Sāmaveda Saṃhitā",
            brahmanas: ["Pañcaviṃśa Brāhmaṇa", "Ṣaḍviṃśa Brāhmaṇa", "Jaiminīya Brāhmaṇa"],
            aranyakas: ["Jaiminīya Āraṇyaka traditions"],
            upanishads: ["Chāndogya Upaniṣad", "Kena Upaniṣad"],
            stats: { primaryFunction: "liturgical chant" }
          },
          notes: "Foundational for sacred music, chant structure, and liturgical sound.",
          relatedNodes: ["gandharvaveda", "chandas", "natyasastra"],
          aigaaneLink: aigaaneLinks.samaveda
        }),
        veda("atharvaveda", "Atharvaveda", {
          essence: "The Veda of healing, protection, royal rites, domestic concerns, metaphysical hymns, and contemplative speculation.",
          keywords: ["atharvaveda", "healing", "protection", "royal rites", "mundaka", "mandukya"],
          sakhas: ["Śaunaka", "Paippalāda"],
          components: {
            samhita: "Atharvaveda Saṃhitā",
            brahmanas: ["Gopatha Brāhmaṇa"],
            aranyakas: "None / not present in the standard Atharvaveda tradition.",
            upanishads: ["Muṇḍaka", "Māṇḍūkya", "Praśna"],
            stats: { survivingMajorSakhas: 2 }
          },
          notes: "Connects household, healing, polity, mantra, and late Vedic reflection.",
          relatedNodes: ["ayurveda", "jyotisha", "vedanta"]
        }),
        node("muktika-appendix", "Muktika Appendix", "appendix", "sruti", "upanishad-canon", "appendix", {
          essence: "Traditional appendix listing 108 Upaniṣads by Vedic affiliation.",
          keywords: ["muktika", "upanishad", "108 upanishads", "canon", "appendix"],
          components: {
            summary: "The Muktika tradition organizes 108 Upaniṣads across Ṛgveda, Śukla Yajurveda, Kṛṣṇa Yajurveda, Sāmaveda, and Atharvaveda affiliations.",
            affiliationCounts: {
              rigveda: 10,
              suklaYajurveda: 19,
              krishnaYajurveda: 32,
              samaveda: 16,
              atharvaveda: 31
            }
          },
          notes: "Detailed list may be expanded later; this node intentionally summarizes rather than listing all 108.",
          relatedNodes: ["vedanta", "yajurveda", "atharvaveda"]
        })
      ]
    }),
    node("smriti", "SMṚTI", "top-level", "smriti", "smriti", "remembered", {
      essence: "Remembered tradition: narrative, law, ritual manuals, philosophy, Purāṇic cosmology, devotion, and applied sacred culture.",
      keywords: ["smriti", "tradition", "dharma", "purana", "itihasa"],
      children: [
        node("vedangas", "Vedāṅgas", "discipline-group", "smriti", "vedanga", "auxiliary", {
          essence: "Six auxiliary disciplines for preserving, interpreting, and performing Vedic knowledge.",
          keywords: ["vedanga", "phonetics", "grammar", "meter", "ritual", "jyotisha"],
          items: ["Śikṣā", "Chandas", "Vyākaraṇa", "Nirukta", "Jyotiṣa", "Kalpa"],
          notes: "Pāṇini's Aṣṭādhyāyī is central to Vyākaraṇa; Piṅgala is central to Chandas.",
          children: [
            node("shiksha", "Śikṣā", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "Phonetics and phonology for accurate Vedic recitation.",
              keywords: ["shiksha", "phonetics", "recitation", "sound", "accent"],
              items: ["Varṇa", "Svara", "Mātrā", "Bala", "Sāman", "Santāna"],
              relatedNodes: ["samaveda", "vyakarana"]
            }),
            node("chandas", "Chandas", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "The discipline of meter, syllabic weight, prosody, and poetic rhythm.",
              keywords: ["chandas", "meter", "laghu", "guru", "pingala", "prosody"],
              items: ["Laghu", "Guru", "Mātrā", "Gaṇa", "Piṅgala tradition"],
              notes: "Useful for understanding Vedic and classical metrical structure.",
              relatedNodes: ["rigveda", "samaveda", "gandharvaveda"],
              aigaaneLink: aigaaneLinks.chandas
            }),
            node("vyakarana", "Vyākaraṇa", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "Grammar and linguistic analysis for preserving and interpreting Sanskrit.",
              keywords: ["vyakarana", "grammar", "panini", "ashtadhyayi", "sanskrit"],
              foundationalText: "Pāṇini's Aṣṭādhyāyī",
              majorCommentaries: ["Mahābhāṣya of Patañjali", "Kāśikā-vṛtti"],
              relatedNodes: ["nirukta", "shiksha"]
            }),
            node("nirukta", "Nirukta", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "Etymology and semantic explanation of Vedic words.",
              keywords: ["nirukta", "etymology", "yaska", "vedic words"],
              foundationalText: "Yāska's Nirukta",
              relatedNodes: ["vyakarana", "rigveda"]
            }),
            node("jyotisha", "Jyotiṣa", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "Ritual timing, calendrics, astral observation, and auspicious alignment.",
              keywords: ["jyotisha", "nakshatra", "tithi", "muhurta", "calendar"],
              foundationalText: "Vedāṅga Jyotiṣa",
              items: ["Tithi", "Nakṣatra", "Muhurta", "Lunar cycles", "Vedic calendar"],
              relatedNodes: ["atma", "atharvaveda"],
              aigaaneLink: aigaaneLinks.jyotisha
            }),
            node("kalpa", "Kalpa", "vedanga", "smriti", "vedanga", "auxiliary", {
              essence: "Ritual procedure, domestic rites, śrauta rites, dharma rules, and altar geometry.",
              keywords: ["kalpa", "shrauta", "grihya", "dharma sutra", "sulba"],
              items: ["Śrauta Sūtras", "Gṛhya Sūtras", "Dharma Sūtras", "Śulba Sūtras"],
              relatedNodes: ["yajurveda", "dharmasastras"]
            })
          ]
        }),
        node("itihasas", "Itihāsas", "epic", "smriti", "itihasa", "major", {
          essence: "Sacred histories presenting dharma through narrative, character, conflict, and divine descent.",
          keywords: ["itihasa", "ramayana", "mahabharata", "gita", "dharma"],
          items: ["Rāmāyaṇa", "Mahābhārata", "Bhagavad Gītā", "Harivaṃśa"],
          notes: "The Bhagavad Gītā stands inside the Mahābhārata as a compact theological and yogic teaching.",
          relatedNodes: ["dharma", "vedanta", "bhakti-vangmaya"]
        }),
        node("puranas", "Purāṇas", "purana-group", "smriti", "purana", "major", {
          essence: "Purāṇic literature teaches cosmology, avatāra, genealogy, pilgrimage, ritual, devotion, sacred time, and narrative theology.",
          keywords: ["purana", "mahapurana", "upapurana", "cosmology", "lokas", "narakas"],
          notes: "Purāṇic classification varies by tradition; the guṇa grouping below follows a common received schema.",
          relatedNodes: ["lokas-studio", "bhakti-vangmaya", "itihasas"],
          aigaaneLink: aigaaneLinks.puranas,
          children: [
            node("mahapuranas", "Mahāpurāṇas", "purana-collection", "smriti", "purana", "major", {
              essence: "The eighteen great Purāṇas grouped here by a traditional guṇa classification.",
              keywords: ["mahapurana", "eighteen puranas", "sattvika", "rajasika", "tamasika"],
              groups: [
                {
                  name: "Sāttvika Purāṇas",
                  gunaClassification: "sattva",
                  texts: ["Viṣṇu", "Bhāgavata", "Nārada", "Garuḍa", "Padma", "Varāha"]
                },
                {
                  name: "Rājasika Purāṇas",
                  gunaClassification: "rajas",
                  texts: ["Brahma", "Brahmāṇḍa", "Brahmavaivarta", "Mārkaṇḍeya", "Bhaviṣya", "Vāmana"]
                },
                {
                  name: "Tāmasika Purāṇas",
                  gunaClassification: "tamas",
                  texts: ["Śiva or Vāyu", "Liṅga", "Skanda", "Agni", "Matsya", "Kūrma"]
                }
              ],
              relatedNodes: ["puranas", "lokas-studio"]
            }),
            node("upapuranas", "Upapurāṇas", "purana-collection", "smriti", "purana", "secondary", {
              essence: "Secondary Purāṇic works expanding local, sectarian, ritual, and narrative traditions.",
              keywords: ["upapurana", "secondary purana", "nrisimha", "devi", "kalki"],
              items: ["Nṛsiṃha Purāṇa", "Sanatkumāra Purāṇa", "Śiva-rahasya", "Devī Purāṇa", "Kalki Purāṇa"],
              notes: "Lists vary widely across textual traditions."
            })
          ]
        }),
        node("dharmasastras", "Dharmaśāstras", "law", "smriti", "dharma", "normative", {
          essence: "Texts on dharma, conduct, rites, social duties, jurisprudence, penance, and life-stage obligations.",
          keywords: ["dharmashastra", "dharma", "law", "smriti", "achara"],
          items: ["Manusmṛti", "Yājñavalkya Smṛti", "Nārada Smṛti", "Parāśara Smṛti", "Gautama Dharma Sūtra", "Āpastamba Dharma Sūtra"],
          notes: "Historically interpreted through commentaries, region, custom, and institutional context.",
          relatedNodes: ["kalpa", "itihasas"]
        }),
        node("darshanas", "Ṣaḍ Darśanas", "philosophy-group", "smriti", "darshana", "classical", {
          essence: "Six classical philosophical systems reasoning about reality, knowledge, liberation, causality, ritual, and consciousness.",
          keywords: ["darshana", "philosophy", "nyaya", "vedanta", "sankhya", "yoga"],
          children: [
            node("nyaya", "Nyāya", "darshana", "smriti", "darshana", "classical", {
              essence: "A system centered on logic, debate, valid cognition, and inference.",
              keywords: ["nyaya", "logic", "inference", "anumana", "pramana"],
              foundationalText: "Gautama's Nyāya Sūtra",
              majorCommentaries: ["Vātsyāyana Bhāṣya", "Uddyotakara's Vārttika", "Vācaspati Miśra", "Udayana", "Gaṅgeśa"],
              relatedNodes: ["anumana", "vaisheshika"],
              aigaaneLink: aigaaneLinks.nyaya
            }),
            node("vaisheshika", "Vaiśeṣika", "darshana", "smriti", "darshana", "classical", {
              essence: "A realist system of categories, substances, qualities, motion, universals, particularity, and inherence.",
              keywords: ["vaisheshika", "kanada", "atomism", "categories", "padartha"],
              foundationalText: "Kaṇāda's Vaiśeṣika Sūtra",
              majorCommentaries: ["Praśastapāda Bhāṣya", "Śrīdhara", "Udayana"],
              relatedNodes: ["nyaya"]
            }),
            node("sankhya", "Sāṃkhya", "darshana", "smriti", "darshana", "classical", {
              essence: "A dualist analysis of puruṣa and prakṛti, guṇas, tattvas, bondage, and discriminative liberation.",
              keywords: ["sankhya", "samkhya", "prakriti", "purusha", "guna", "tattva"],
              foundationalText: "Sāṃkhya Kārikā as the earliest extant systematic exposition; Sāṃkhya Sūtras as a later attributed aphoristic tradition.",
              majorCommentaries: ["Gauḍapāda Bhāṣya", "Vācaspati Miśra's Tattvakaumudī", "Yuktidīpikā"],
              notes: "The Sāṃkhya Kārikā is the earliest extant systematic exposition; Sāṃkhya Sūtras represent a later attributed aphoristic tradition.",
              relatedNodes: ["yoga", "vedanta"]
            }),
            node("yoga", "Yoga", "darshana", "smriti", "darshana", "classical", {
              essence: "A discipline of citta, meditation, ethics, samādhi, and liberation closely related to Sāṃkhya metaphysics.",
              keywords: ["yoga", "patanjali", "citta", "samadhi", "ashtanga"],
              foundationalText: "Patañjali's Yoga Sūtra",
              majorCommentaries: ["Vyāsa Bhāṣya", "Vācaspati Miśra's Tattvavaiśāradī", "Vijñānabhikṣu"],
              relatedNodes: ["sankhya", "upanishad"]
            }),
            node("purva-mimamsa", "Pūrva Mīmāṃsā", "darshana", "smriti", "darshana", "classical", {
              essence: "A hermeneutic and ritual-philosophical system focused on Vedic injunction, dharma, language, and action.",
              keywords: ["mimamsa", "jaimini", "ritual", "dharma", "hermeneutics"],
              foundationalText: "Jaimini's Mīmāṃsā Sūtra",
              majorCommentaries: ["Śabara Bhāṣya", "Kumārila Bhaṭṭa", "Prabhākara"],
              relatedNodes: ["yajurveda", "kalpa", "dharmasastras"]
            }),
            node("vedanta", "Vedānta", "darshana", "smriti", "darshana", "classical", {
              essence: "The Upaniṣadic philosophical stream focused on Brahman, self, liberation, and interpretation of the Brahma Sūtra.",
              keywords: ["vedanta", "brahman", "atman", "upanishad", "shankara", "ramanuja", "madhva"],
              foundationalText: "Bādarāyaṇa's Brahma Sūtra",
              majorCommentaries: ["Śaṅkara Bhāṣya", "Rāmānuja's Śrī Bhāṣya", "Madhva Bhāṣya", "Nimbārka", "Vallabha"],
              relatedNodes: ["upanishad", "muktika-appendix", "bhagavad-gita"],
              aigaaneLink: aigaaneLinks.vedanta
            })
          ]
        }),
        node("upavedas", "Upavedas", "applied-knowledge-group", "smriti", "upaveda", "applied", {
          essence: "Applied sciences traditionally linked with the Vedic world.",
          keywords: ["upaveda", "ayurveda", "dhanurveda", "gandharvaveda", "sthaptya"],
          children: [
            node("ayurveda", "Āyurveda", "upaveda", "smriti", "upaveda", "applied", {
              essence: "Medical and life-science knowledge concerned with health, balance, disease, diet, and longevity.",
              keywords: ["ayurveda", "medicine", "health", "dosha", "charaka"],
              foundationalText: "Caraka Saṃhitā and Suśruta Saṃhitā traditions",
              majorCommentaries: ["Cakrapāṇidatta", "Dalhaṇa"]
            }),
            node("dhanurveda", "Dhanurveda", "upaveda", "smriti", "upaveda", "applied", {
              essence: "Martial knowledge, archery, warfare, discipline, and protective skill.",
              keywords: ["dhanurveda", "archery", "martial", "warfare"],
              notes: "Survives in scattered textual and traditional references."
            }),
            node("gandharvaveda", "Gāndharvaveda", "upaveda", "smriti", "upaveda", "applied", {
              essence: "Music, performance, sound, and aesthetic experience.",
              keywords: ["gandharvaveda", "music", "rasa", "sound", "performance"],
              items: ["Gāna", "Vādya", "Nāṭya", "Rasa", "Melodic discipline"],
              relatedNodes: ["samaveda", "natyasastra"],
              aigaaneLink: aigaaneLinks.gandharvaveda
            }),
            node("sthapatyaveda", "Sthāpatyaveda", "upaveda", "smriti", "upaveda", "applied", {
              essence: "Architecture, sacred layout, image-making, building, and spatial design.",
              keywords: ["sthaptya", "vastu", "architecture", "temple", "murti"],
              relatedNodes: ["agamas-tantras"]
            })
          ]
        }),
        node("agamas-tantras", "Āgamas & Tantras", "practice-group", "smriti", "agama", "sectarian-practice", {
          essence: "Temple, mantra, deity, yoga, initiation, ritual, and subtle-body traditions across Vaiṣṇava, Śaiva, Śākta, and other streams.",
          keywords: ["agama", "tantra", "mantra", "temple", "diksha", "sri vidya"],
          notes: "Representative list only; full sectarian corpora are much larger.",
          children: [
            node("vaishnava-agamas", "Vaiṣṇava Āgamas", "agama-branch", "smriti", "agama", "sectarian-practice", {
              essence: "Vaiṣṇava ritual, temple, icon, mantra, and theology traditions.",
              keywords: ["vaishnava agama", "pancaratra", "vaikhanasa", "vishnu"],
              items: ["Pāñcarātra Saṃhitās", "Vaikhānasa texts", "Nārada Pāñcarātra", "Jayākhya Saṃhitā"]
            }),
            node("shaiva-agamas", "Śaiva Āgamas", "agama-branch", "smriti", "agama", "sectarian-practice", {
              essence: "Śaiva ritual, yoga, mantra, temple, and nondual or dual Śaiva traditions.",
              keywords: ["shaiva agama", "shiva sutras", "vijnana bhairava", "mrgendra"],
              items: ["Kāmika Āgama", "Mṛgendra Āgama", "Śiva Sūtras", "Vijñāna Bhairava Tantra"]
            }),
            node("shakta-tantras", "Śākta Tantras", "tantra-branch", "smriti", "agama", "sectarian-practice", {
              essence: "Śākta mantra, deity, ritual, subtle-body, Śrī Vidyā, and goddess-centered traditions.",
              keywords: ["shakta tantra", "kularnava", "tripura rahasya", "lalita sahasranama", "sri vidya"],
              items: ["Kularṇava Tantra", "Tripurā Rahasya", "Lalitā Sahasranāma / Śrī Vidyā notes", "Tantrarāja Tantra"]
            })
          ]
        }),
        node("bhakti-vangmaya", "Bhakti Sādhana Vāṅmaya", "devotional-literature-group", "smriti", "bhakti", "devotional", {
          essence: "Devotional literature for practice, song, remembrance, theology, and surrender.",
          keywords: ["bhakti", "devotion", "vernacular", "kirtan", "poetry"],
          notes: "Representative works only.",
          children: [
            node("sanskrit-bhakti", "Sanskrit Bhakti", "devotional-literature", "smriti", "bhakti", "devotional", {
              essence: "Sanskrit devotional works and theological poetry.",
              keywords: ["sanskrit bhakti", "gita govinda", "narada bhakti sutra"],
              items: ["Gīta Govinda", "Nārada Bhakti Sūtra", "Śāṇḍilya Bhakti Sūtra", "Stotra literature"]
            }),
            node("tamil-bhakti", "Tamil Bhakti", "devotional-literature", "smriti", "bhakti", "devotional", {
              essence: "Tamil Vaiṣṇava and Śaiva devotional canons.",
              keywords: ["tamil bhakti", "divya prabandham", "tevaram", "alvar", "nayanmar"],
              items: ["Divya Prabandham", "Tēvāram", "Tiruvācakam", "Tiruvāymoḻi"]
            }),
            node("marathi-bhakti", "Marathi Bhakti", "devotional-literature", "smriti", "bhakti", "devotional", {
              essence: "Vārkarī and Marathi devotional streams.",
              keywords: ["marathi bhakti", "jnaneshwari", "tukaram", "abhang"],
              items: ["Jñāneśvarī", "Tukārām Gāthā", "Abhaṅgas", "Eknāthī Bhāgavata"]
            }),
            node("hindi-bhakti", "Hindi Bhakti", "devotional-literature", "smriti", "bhakti", "devotional", {
              essence: "North Indian devotional poetry and retellings.",
              keywords: ["hindi bhakti", "ramcharitmanas", "surdas", "tulsidas", "kabir"],
              items: ["Rāmcaritmānas", "Sūrsāgar", "Kabīr poetry", "Vinaya Patrikā"]
            }),
            node("bengali-bhakti", "Bengali Bhakti", "devotional-literature", "smriti", "bhakti", "devotional", {
              essence: "Bengali Vaiṣṇava devotional theology, biography, and song.",
              keywords: ["bengali bhakti", "chaitanya", "charitamrita", "gaudiya"],
              items: ["Caitanya-caritāmṛta", "Caitanya-bhāgavata", "Padāvalī kīrtana"]
            }),
            node("regional-note", "Regional Bhakti Note", "devotional-note", "smriti", "bhakti", "representative", {
              essence: "Regional-language bhakti corpora are vast and locally rooted.",
              keywords: ["regional bhakti", "vernacular", "representative"],
              notes: "Representative works only; this tree can expand later for Kannada, Telugu, Odia, Gujarati, Assamese, Malayalam, and other traditions."
            })
          ]
        }),
        node("independent-granths", "Independent Advaita / Bhakti Granths", "granth-group", "smriti", "granth", "commentarial-devotional", {
          essence: "Influential standalone works of philosophy, practice, and devotion.",
          keywords: ["advaita", "bhakti", "granth", "shankara", "ramanuja", "madhva"],
          items: ["Vivekacūḍāmaṇi", "Ātma-bodha", "Upadeśa Sāhasrī", "Vedānta Sāra", "Śrī Bhāṣya", "Gītā Bhāṣyas", "Bhakti-rasāmṛta-sindhu"],
          notes: "Includes works associated with Śaṅkara, Rāmānuja, Madhva, and later teachers.",
          relatedNodes: ["vedanta", "bhakti-vangmaya"]
        })
      ]
    }),
    node("secular-supporting", "SECULAR / SUPPORTING TEXTS", "top-level", "secular", "secular", "supporting", {
      essence: "Classical knowledge systems supporting polity, arts, ethics, poetics, social life, omens, and narrative education.",
      keywords: ["secular", "supporting texts", "artha", "natya", "kama", "pancatantra"],
      notes: "These are culturally important supporting texts but not the same authority class as Śruti.",
      children: [
        node("arthasastra", "Arthaśāstra", "statecraft", "secular", "supporting-text", "classical", {
          essence: "Treatise on polity, governance, economics, diplomacy, law, and statecraft.",
          keywords: ["arthashastra", "kautilya", "chanakya", "statecraft", "politics"],
          items: ["Kauṭilya / Cāṇakya tradition"],
          notes: "A political science text and supporting knowledge source."
        }),
        node("natyasastra", "Nāṭyaśāstra", "arts", "secular", "supporting-text", "classical", {
          essence: "Foundational treatise on drama, performance, rasa, music, gesture, staging, and aesthetics.",
          keywords: ["natyashastra", "rasa", "bharata", "performance", "music"],
          items: ["Bharata Muni", "Rasa theory", "Abhinaya", "Gāna", "Nāṭya"],
          relatedNodes: ["gandharvaveda", "bhakti-vangmaya"]
        }),
        node("kamasutra", "Kāma Sūtra", "social-art", "secular", "supporting-text", "classical", {
          essence: "Classical text on kāma, refined social life, relationships, aesthetics, and household culture.",
          keywords: ["kamasutra", "kama", "social life", "aesthetics"],
          notes: "Best read in its broader puruṣārtha context, not as a single-topic manual."
        }),
        node("brhat-samhita", "Bṛhat Saṃhitā", "encyclopedic", "secular", "supporting-text", "classical", {
          essence: "Varāhamihira's encyclopedic compendium on astral omens, architecture, weather, gems, rituals, and cultural sciences.",
          keywords: ["brhat samhita", "varahamihira", "omens", "architecture", "weather"],
          relatedNodes: ["jyotisha", "sthapatyaveda"]
        }),
        node("pancatantra-hitopadesha", "Pañcatantra / Hitopadeśa", "narrative", "secular", "supporting-text", "classical", {
          essence: "Didactic story collections teaching practical wisdom, ethics, diplomacy, and human behavior through narrative.",
          keywords: ["pancatantra", "hitopadesha", "fables", "niti", "wisdom"],
          notes: "Widely transmitted across languages and cultures."
        })
      ]
    })
  ]
};

export const scriptureCategories = [
  { id: "all", label: "All", matches: ["taxonomy", "sruti", "smriti", "secular", "veda", "vedanga", "itihasa", "purana", "dharma", "darshana", "upaveda", "agama", "bhakti", "granth", "supporting-text", "upanishad-canon"] },
  { id: "sruti", label: "Śruti", matches: ["sruti", "veda", "upanishad-canon"] },
  { id: "smriti", label: "Smṛti", matches: ["smriti", "vedanga", "itihasa", "purana", "dharma", "darshana", "upaveda", "agama", "bhakti", "granth"] },
  { id: "secular", label: "Secular", matches: ["secular", "supporting-text"] },
  { id: "veda", label: "Vedas", matches: ["veda"] },
  { id: "purana", label: "Purāṇas", matches: ["purana"] },
  { id: "darshana", label: "Darśanas", matches: ["darshana"] },
  { id: "agama", label: "Āgamas", matches: ["agama"] },
  { id: "aigaane-link", label: "Aigaane Links", matches: ["aigaane-link"] }
];

export const scriptureGlossary = {
  "Śruti": "That which is heard; revealed Vedic scripture.",
  "Smṛti": "That which is remembered; tradition, law, narrative, and interpretive literature.",
  "Śākhā": "A Vedic recension or branch of transmission.",
  "Saṃhitā": "Collected mantra layer of a Veda.",
  "Brāhmaṇa": "Ritual and theological explanation of Vedic practice.",
  "Āraṇyaka": "Forest text bridging ritual symbolism and contemplation.",
  "Upaniṣad": "Philosophical and contemplative teaching on ultimate reality, self, and liberation.",
  "Vedāṅga": "Auxiliary discipline of Vedic learning.",
  "Darśana": "Philosophical viewpoint or system.",
  "Purāṇa": "Ancient narrative text with cosmology, genealogy, pilgrimage, devotion, and sacred history.",
  "Āgama": "Scriptural stream for temple, mantra, deity, and ritual practice.",
  "Tantra": "Practice-oriented scripture involving mantra, deity, body, ritual, initiation, and realization."
};
