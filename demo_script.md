# LociLoom: 3-Minute Viva Presentation & Examiner Q&A Script

**Project Title:** LociLoom: An AI-Based Personalized Memory Palace Generator for Adaptive Learning  
**Tagline:** *"Weave your notes into a story you can walk through."*  
**Audience:** External University Viva Examiners, Project Review Committee, Academic Evaluators  

---

## ⏱️ 3-Minute Live Demonstration Walkthrough

### Minute 1: The Problem & The Memory Palace Generation (Pages 1 & 2)
- **Presenter Action:** Open browser to `http://localhost:8501`. Show the Landing Page with its clean, bright light theme and 3-step explanation. Click **Create Palace** in the sidebar.
- **Presenter Pitch:**  
  > *"Respected examiners, when students prepare for exams, they typically resort to passive rote reading—which yields a steep forgetting curve where up to 70% of material is forgotten within 48 hours. Classical cognitive science offers a proven antidote: the 2,500-year-old Method of Loci, or Memory Palace. However, manually converting abstract lecture notes into vivid spatial journeys is mentally exhausting. LociLoom automates this entire cognitive pipeline 100% locally on CPU without paid APIs."*
- **Presenter Action:** Click the **Photosynthesis (Biology)** preset. Point out the auto-detected topic (*Biology, confidence 94%*), select the **Cozy Modern House** template, choose the **Dramatic** story style, and click **Weave My Memory Palace**.
- **Presenter Pitch:**  
  > *"Within 500 milliseconds, LociLoom has sanitized the text, extracted the core concepts using spaCy and TF-IDF while strictly preserving their chronological order, estimated their cognitive difficulty using an 8-feature Random Forest model (81.6% CV accuracy), mapped abstract ideas into sensory anchors using a 3-tier dictionary and phonetic fallback, and allocated them sequentially along the 2D floorplan. Notice the interactive Plotly map where students can step through their journey."*

---

### Minute 2: Active Retrieval Practice & Spaced Repetition (Pages 3 & 4)
- **Presenter Action:** Navigate to **Practice Quiz**. Select the generated Biology Palace. Choose question type **Type Concept**.
- **Presenter Pitch:**  
  > *"Encoding is only half the battle; retrieval practice is essential for long-term consolidation. LociLoom offers four adaptive question formats. When the student types an answer, we evaluate it using `rapidfuzz` token-sort distance with a 75% threshold, accommodating minor misspellings while rewarding conceptual grasp. If stuck, our 2-step hint system reveals letter masks and spatial palace clues."*
- **Presenter Action:** Type `chloroplasts` (with a slight typo `chloroplast`), submit, and show the instant feedback and SM-2 quality calculation. Then switch to **Revision Planner**.
- **Presenter Pitch:**  
  > *"Every retrieval attempt feeds our Spaced Repetition Engine. We implement Piotr Wozniak's SM-2 algorithm, adjusting the Ease Factor and intervals. But we also train a calibrated Logistic Regression forgetting curve model (92.8% accuracy, 0.975 ROC-AUC) that outperforms fixed-interval baselines, projecting memory lapse risks across 24-hour, 3-day, and 7-day horizons so students review right before memory decay accelerates."*

---

### Minute 3: Scientific Experiment Mode & Accessibility (Pages 6 & 7)
- **Presenter Action:** Navigate to **Experiment Mode**. Show the counterbalanced protocol: Condition A (Standard Linear Notes) vs. Condition B (LociLoom Memory Palace).
- **Presenter Pitch:**  
  > *"To ensure scientific rigor, LociLoom embeds an empirical testing lab. A student or researcher can run randomized, counterbalanced within-subject trials. LociLoom records immediate and 24-hour delayed recall, automatically computing paired Student's t-tests, Wilcoxon signed-rank tests, and Cohen's d effect sizes with honest sample-size power warnings."*
- **Presenter Action:** Quickly click **Settings & Accessibility** to demonstrate the OpenDyslexic font toggle and High-Contrast Light Mode, then conclude.
- **Presenter Pitch:**  
  > *"Finally, LociLoom adheres strictly to universal design: Dyslexia-friendly typography, high-contrast light styling, screen-reader text alternatives, and local SQLite data isolation with zero cloud telemetry. In summary, LociLoom bridges ancient cognitive memory science with modern machine learning to make adaptive studying effortless, private, and engaging. Thank you, and I welcome your questions."*

---

## 🎓 Viva Examiner Q&A Defense Guide

### Q1: Why did you build LociLoom in a 2D desktop format when literature on Memory Palaces often highlights 3D Virtual Reality?
**Model Answer:**
- **Honest Academic Disclosure:** Pioneering studies like Krokos et al. (2018) and Moll & Sykes (2022) examined immersive HMD-VR or physical architectural environments.
- **Practical & Accessibility Rationale:** Immersive VR requires expensive headsets (Meta Quest, HTC Vive) and causes motion simulator sickness in up to 30% of students.
- **Cognitive Science Basis:** Allan Paivio's Dual Coding Theory and Baddeley's visuospatial scratchpad demonstrate that even 2D schematics and structured spatial route maps double the retrieval pathways (verbal + visual) compared to plain linear text.
- **Empirical Harness:** We built **Experiment Mode** specifically so educational institutions can quantitatively evaluate how much benefit the 2D interactive representation provides.

---

### Q2: How does your Concept Difficulty Model work, and why did Random Forest win over Logistic Regression?
**Model Answer:**
- **Feature Engineering:** We extract 8 distinct cognitive and linguistic features from each concept:
  1. `word_count` (phrase complexity)
  2. `char_length` (visual word length)
  3. `syllable_count` (articulatory phonological loop load)
  4. `abstractness_score` (lexicon tangibility metric)
  5. `word_rarity_score` (corpus frequency inverse)
  6. `has_digits` (presence of numbers/chemical formulas)
  7. `sentence_length` (contextual density)
  8. `topic_code` (domain-specific difficulty baseline)
- **Model Evaluation:** Naive dummy baseline achieves 34.2%. Logistic Regression achieves 73.5%. Random Forest achieved **81.63% 5-fold cross-validation accuracy** because cognitive difficulty exhibits non-linear feature interactions (e.g., a word with high syllables is disproportionately harder if it is also rare and abstract).

---

### Q3: How do you map abstract terms like "Inflation" or "Polymorphism" to physical objects without an internet connection?
**Model Answer:**
- We developed a **3-tier cascading mapping pipeline**:
  1. **Tier 1 (Curated Dictionary)**: Hand-curated dictionary of 245+ educational concepts mapped to sensory, tactile items (e.g., *Inflation* → expanding balloon bursting under pressure).
  2. **Tier 2 (Semantic Cosine Similarity)**: TF-IDF vectorizer over dictionary concepts to find nearest conceptual neighbors.
  3. **Tier 3 (Phonetic & Morphological Fallback)**: Prefix analysis (e.g., *Poly-* → beaded chain, *Micro-* → brass microscope) and sound-alike phonetic rhyming rules (e.g., *Isomorphism* → ice prism).
- This guarantees 100% offline determinism and ensures no concept is ever left without an image.

---

### Q4: Why did you choose the SM-2 algorithm, and how does your ML forgetting model improve upon it?
**Model Answer:**
- **SM-2 Strengths:** Piotr Wozniak's SM-2 algorithm is computationally lightweight, deterministic, and widely validated across decades of spaced repetition research. It dynamically adjusts Ease Factors and intervals based on 0–5 quality scores.
- **The Cold-Start & Fixed-Interval Limitation:** Standard SM-2 uses fixed multipliers and cannot assess inter-session lapse probability if a student deviates from the calendar.
- **Our ML Enhancement:** We trained a calibrated Logistic Regression model (92.8% test accuracy, 0.9748 ROC-AUC) on 2,500 study logs. It forecasts forgetting probability across 24-hour, 3-day, and 7-day horizons based on past retrieval accuracy, response latency, concept difficulty, and elapsed time. This allows LociLoom to highlight items at immediate risk of slipping from memory.

---

### Q5: How do you handle student privacy and data security?
**Model Answer:**
- **Zero Cloud Telemetry:** No user notes, quiz attempts, or study habits are transmitted to external servers or cloud APIs.
- **Local Persistence:** Everything is stored in a local SQLite database (`data/lociloom.db`) using strict parameterized queries.
- **Anonymous Sessions:** Students are identified by local pseudonymous tokens (`LL-xxxx-xxxx`) generated in session state, with a one-click local database wipe button in Settings.

---

### Q6: Can students use their own homes instead of the built-in palace templates?
**Model Answer:**
- Yes! On the **Create Palace** page, students can select **Custom Place** under Palace Architecture and enter comma-separated rooms from their own home, hostel, or school (e.g., *My Balcony, Kitchen Sink, Bookshelf, Bed*).
- Our custom parser computes sequential coordinate positions on a winding 2D grid and anchors the concepts to the student's personal physical environment, significantly boosting emotional and spatial familiarity.
