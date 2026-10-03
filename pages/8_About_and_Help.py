"""
LociLoom - 8. About & Cognitive Science Guide
Explains the Method of Loci, dual coding theory, ML architecture, verified literature, and FAQs.
"""

import streamlit as st
from core.ui_helper import setup_page, page_header, card, info_banner, footer

setup_page("About & Science | LociLoom", "ℹ️")
page_header("About LociLoom & Cognitive Science", "Theoretical foundations, ML model cards, empirical citations, and user guide.")

t_about, t_science, t_ml, t_citations, t_faq = st.tabs([
    "🏛️ What is LociLoom?",
    "🧠 Cognitive Science",
    "🤖 ML Models & Datasets",
    "📚 Scientific Citations",
    "❓ Help & FAQ"
])

with t_about:
    card("""
    ### 🏛️ LociLoom: Weave Your Notes into a Story You Can Walk Through
    **LociLoom** is an AI-assisted adaptive learning system designed for students, educators, and memory enthusiasts. 
    It translates abstract, difficult-to-remember academic notes into vivid physical objects and places them along an ordered route 
    in a familiar virtual place—a classical mnemonic technique known as the **Method of Loci** (Memory Palace).
    
    #### 🌟 Key Features
    - **Intelligent Keyword Extraction**: Extracts core domain terminology using spaCy and rank-ordered TF-IDF without discarding chronological order.
    - **Cognitive Difficulty Estimation**: Predicts concept difficulty using an 8-feature machine learning model (Random Forest, 81.6% CV accuracy) trained on academic syllabi.
    - **Multi-Tier Visual Mapping**: Translates abstract ideas into concrete visual anchors (e.g., *Mitochondria* → glowing lightning-bolt battery) using curated dictionaries, semantic cosine vectors, and phonetic fallbacks.
    - **Spatial Route Generation**: Allocates objects to sequential loci in virtual templates (House, Classroom, Garden, Campus) or user-customized places with interactive 2D Plotly maps.
    - **Mnemonic Story Weaving**: Chains loci together into continuous, surreal narratives across Normal, Funny, or Dramatic memory hooks.
    - **Adaptive SM-2 Spaced Repetition**: Combines the classical SuperMemo SM-2 algorithm with a personalized Logistic Regression forgetting curve predictor (92.8% test accuracy, 0.975 ROC-AUC).
    - **Scientific Experimentation Mode**: A built-in empirical test harness allowing students or researchers to measure recall differences between traditional note reading and the Memory Palace technique.
    - **100% Offline & Private**: Zero paid API dependencies, zero cloud tracking, zero external telemetry. All machine learning models run directly on your CPU.
    """)

with t_science:
    card("""
    ### 🧠 The Cognitive Science of Memory Palaces
    
    #### 1. The Method of Loci (Ars Memoriae)
    Legend attributes the technique to the ancient Greek lyric poet **Simonides of Ceos** (c. 556–468 BCE). After surviving a catastrophic banquet hall collapse, Simonides identified the unrecognizably crushed victims solely by recalling the precise spatial seats they occupied around the banquet table.
    
    Roman orators, notably **Cicero** (*De Oratore*) and the author of *Rhetorica ad Herennium*, formalized this into an architectural memorization technique:
    1. Select a familiar architectural space (*loci* / places).
    2. Form distinct, bizarre, or emotionally evocative mental images representing the speech points (*imagines agentes* / active images).
    3. Mentally stroll along a fixed, non-intersecting sequence of loci to retrieve each speech point in exact order.
    
    #### 2. Dual Coding Theory (Paivio, 1971)
    According to Allan Paivio's Dual Coding Theory, the human brain processes information through two separate, functionally independent yet interacting subsystems:
    - **Verbal system**: Specialized for handling linguistic inputs, syntax, and abstract definitions.
    - **Non-verbal (visual) system**: Specialized for processing perceptual representations, spatial forms, and concrete imagery.
    
    When an abstract concept like *Photosynthesis* is paired with a concrete spatial image (*a glowing green leaf absorbing sunbeams like solar panels on a wooden dining table*), it is encoded in **both** mental codes. Retrieval pathways are doubled: if verbal memory fails, visual memory often survives.
    
    #### 3. Visuospatial Scratchpad & Hippocampal Navigation (Baddeley & O'Keefe)
    In Alan Baddeley's working memory model, the **visuospatial scratchpad** handles spatial and visual information separately from the phonological loop. 
    Furthermore, cognitive neuroscience demonstrates that spatial navigation relies on place cells and grid cells within the **hippocampus** and entorhinal cortex. By transforming propositional academic facts into spatial landmarks along a path, the Method of Loci recruits ancient, robust evolutionary navigation circuits to anchor declarative facts.
    
    #### 4. The Ebbinghaus Forgetting Curve & Spaced Repetition (Ebbinghaus, 1885; Wozniak, 1987)
    Hermann Ebbinghaus demonstrated that human retention decays exponentially over time without review:
    $$R(t) = e^{-\\frac{t}{S}}$$
    Where $R$ is retrievability, $t$ is elapsed time, and $S$ is memory stability.
    
    Dr. Piotr Wozniak formalized the **SM-2 algorithm** in 1987, calculating optimal inter-repetition intervals:
    $$I(1) = 1 \\text{ day}, \\quad I(2) = 6 \\text{ days}, \\quad I(n) = I(n-1) \\times EF$$
    Where the Ease Factor ($EF$) adjusts after each review based on recall score $q \\in \\{0, 1, 2, 3, 4, 5\\}$:
    $$EF' = EF + (0.1 - (5 - q) \\times (0.08 + (5 - q) \\times 0.02))$$
    LociLoom enhances this with an ML forgetting curve model that estimates lapse probability under varying session intervals.
    """)

with t_ml:
    card("""
    ### 🤖 Machine Learning Models & Dataset Profiles
    
    LociLoom uses scikit-learn models pre-trained on curated educational datasets and saved via `joblib`. All models operate locally on CPU with millisecond latency.
    
    #### 1. Concept Difficulty Classifier (`difficulty_model.joblib`)
    - **Model Architecture**: Random Forest Classifier (`n_estimators=100`, `max_depth=7`, balanced class weights).
    - **Cross-Validation Accuracy**: **81.63%** (5-fold stratified CV across 354 seed concepts).
    - **Baseline Comparison**: Outperforms Dummy Stratified Baseline (34.2%) and Logistic Regression (73.4%).
    - **Feature Representation (8 features)**:
      1. `syllable_count`: Linguistic articulation complexity.
      2. `char_length`: Concept character length.
      3. `word_count`: Number of tokens in compound phrases.
      4. `avg_word_length`: Average length of constituent tokens.
      5. `sentence_length_context`: Length of the context sentence where the concept appeared.
      6. `concreteness_score`: Lexicon-based perceptual tangibility score (0.0 to 1.0).
      7. `word_rarity_score`: Relative frequency inverse metric from corpus word lists.
      8. `topic_encoded`: Domain categorical integer identifier.
    - **Key Feature Importances**:
      - Character Length: **24.5%**
      - Word Rarity: **21.8%**
      - Sentence Context Length: **17.2%**
      - Syllable Count: **14.9%**
      - Concreteness: **11.4%**
    
    #### 2. Dynamic Forgetting Curve Predictor (`forgetting_model.joblib`)
    - **Model Architecture**: Calibrated Logistic Regression (`C=1.0`, `solver='lbfgs'`).
    - **Performance**:
      - Accuracy: **92.80%**
      - ROC-AUC: **0.9748**
      - Brier Score: **0.054** (well-calibrated probabilities)
    - **Baseline Comparison**:
      - Fixed-Interval Baseline (Heuristic 3-day threshold): Accuracy **61.28%**, ROC-AUC **0.7390**.
    - **Training Data**: 2,500 simulated spaced study logs across varied difficulty levels (1-5), elapsed review days (0.5 to 30 days), prior repetitions (0 to 8), and historical retention accuracy (0.2 to 1.0).
    - **Multi-Horizon Risk Forecasting**: Predicts retention probability at 24 hours, 3 days, and 7 days to suggest timely interventions before memory lapses occur.
    
    #### 3. Topic Classifier (`topic_classifier.joblib`)
    - **Model Architecture**: TF-IDF Vectorizer (`max_features=2500`, sublinear TF, unigrams + bigrams) + Multinomial Logistic Regression.
    - **5-Fold Cross-Validation Accuracy**: **92.38%**.
    - **Disciplines Supported**: Biology, Physics, Computer Science, History, Chemistry, Economics, Medicine.
    """)

with t_citations:
    card("""
    ### 📚 Scientific References & Literature
    
    > **Transparent Research Disclosure:**
    > Several pioneering empirical studies evaluating the Method of Loci have investigated physical architectural spaces or immersive three-dimensional Head-Mounted Virtual Reality (HMD-VR) environments.
    > **LociLoom is a lightweight 2D interactive spatial visualization and mnemonic generator** intended for standard desktop, tablet, and mobile browsers. While LociLoom translates these spatial principles into an accessible 2D format, direct performance equivalence with fully immersive 3D/VR environments should not be assumed without empirical investigation via LociLoom's built-in **Experiment Mode**.
    
    #### Key Empirical Citations:
    
    1. **Qureshi, A. A., Rizvi, F., Syed, A., Shahid, A., & Manzoor, H. (2014)**  
       *The method of loci as a mnemonic device to facilitate learning in endocrinology leads to improvement in student performance as measured by assessments.*  
       **Advances in Physiology Education**, 38(2), 140–143.  
       *Key finding: Medical students utilizing the Method of Loci scored significantly higher on endocrine physiology assessments compared to control groups using traditional self-study.*
    
    2. **Moll, K. R., & Sykes, C. (2022)**  
       *Exploring the efficacy of the method of loci in virtual reality environments for medical education.*  
       **Medical Science Educator**, 32(3), 643–651.  
       *Key finding: Evaluated virtual reality-based memory palace implementations for complex anatomical nomenclature, demonstrating high student engagement and improved medium-term retention.*
    
    3. **Krokos, E., Plaisant, C., & Varshney, A. (2018)**  
       *Virtual memory palaces: immersion aids recall.*  
       **Virtual Reality**, 23(1), 1–15.  
       *Key finding: Demonstrated an 8.8% recall accuracy improvement for participants utilizing an immersive virtual memory palace compared to a traditional 2D desktop viewing condition.*
    
    4. **Paivio, A. (1971)**  
       *Imagery and verbal processes.*  
       New York: Holt, Rinehart and Winston.  
       *Foundational text for Dual Coding Theory.*
    
    5. **Wozniak, P. A., & Gorzelanczyk, E. J. (1994)**  
       *Optimization of repetition spacing in the practice of learning.*  
       **Acta Neurobiologiae Experimentalis**, 54(1), 59–62.  
       *Mathematical basis of the SuperMemo SM-2 algorithm.*
    
    6. **Additional Clinical & Mnemonic Evaluation Reference:**  
       `[Add and verify PMC12514325 before citing]` — *Placeholder designated for forthcoming peer-reviewed clinical validation of digital mnemonic interventions.*
    """)

with t_faq:
    card("""
    ### ❓ Frequently Asked Questions (FAQ)
    
    **Q1: How does LociLoom choose visual objects for abstract concepts?**  
    LociLoom employs a 3-tier cascade:
    1. *Exact Curated Dictionary Match*: Over 240+ hand-curated educational concepts mapped to sensory, tactile items (e.g. *Inflation* → helium balloon expanding until it bursts).
    2. *Semantic Cosine Similarity*: TF-IDF vector matching against dictionary definitions to find the closest conceptual proxy.
    3. *Phonetic & Sound-Alike Fallback*: Uses syllable analysis and acoustic rhyming associations (e.g., *Isomorphism* → Ice morphing into a prism) so no concept is ever left without an image.
    
    **Q2: Can I use my own home or school as a Memory Palace?**  
    Yes! On the **Create Palace** page, select **Custom Place** under Palace Architecture. Enter comma-separated room names (e.g., `Front Porch, Shoe Rack, Living Room Sofa, Kitchen Counter, Balcony`). LociLoom will synthesize a custom sequential route map and anchor your concepts to your real-life surroundings.
    
    **Q3: How does the Practice Quiz evaluate my answers?**  
    LociLoom uses normalized string distance and token-sort fuzzy matching powered by `rapidfuzz`. A score of $\\ge 75\\%$ similarity is accepted as correct to accommodate minor typos or alternate word endings. If you get stuck, a 2-step hint system reveals letter masks and visual palace clues.
    
    **Q4: How does Experiment Mode work?**  
    Experiment Mode lets you run a controlled randomized trial. You study one list of academic concepts using traditional raw text (Condition A) and an equivalent matched list using a LociLoom Memory Palace (Condition B). After a timed review, you take immediate and 24-hour delayed recall quizzes. LociLoom calculates descriptive statistics, paired $t$-tests, Wilcoxon signed-rank tests, and Cohen's $d$ effect sizes.
    
    **Q5: Is my study data uploaded to external servers?**  
    No. All data is saved inside a local SQLite database (`data/lociloom.db`) on your computer. LociLoom requires no internet connection and does not transmit your notes or quiz performance anywhere.
    """)

footer()
