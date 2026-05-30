# Biodiversity in National Parks

Exploratory data analysis of species conservation status across four US national parks. Investigates whether certain species categories are disproportionately at risk and how conservation risk is distributed across parks.

---

## Key Findings

- **Mammals (17%) and Birds (15.4%)** are the most at-risk categories — confirmed statistically via chi-square (χ²=426.67, p<0.0001)
- **Birds drive the signal by volume** (75 at-risk species); **Mammals by severity** (6 Endangered — the most of any category)
- **Fish are underappreciated**: 64% of at-risk fish hold Threatened or Endangered status
- **All four parks show near-identical risk profiles** (2.6–2.8%) — risk is systemic at species level, not geographic
- **Yellowstone** has the highest endangered species observation activity (1,228 recorded observations)

---

## Data

| File | Rows | Description |
|---|---|---|
| `species_info.csv` | 5,824 | Species with category, scientific name, common names, conservation status |
| `observations.csv` | 23,296 | Observation counts per species per park (4 parks × 5,541 species) |

**Parks covered:** Bryce, Yellowstone, Yosemite, Great Smoky Mountains

**Data note:** Observation counts reflect recorded activity per species per park. Survey effort is unknown — counts should not be interpreted as population size or abundance.

---

## Setup

```bash
conda create -n biodiversity-in-national-parks python=3.12.7
conda activate biodiversity-in-national-parks
pip install pandas numpy matplotlib seaborn scipy jupyter
```

---

## Run

```bash
conda activate biodiversity-in-national-parks
jupyter notebook biodiversity.ipynb
```

Run all cells top to bottom. No external data download required — both CSVs are included in the repo.

---

## Notebook Structure

| Section | Description |
|---|---|
| 1. Setup | Imports and plot styling |
| 2. Load & Clean | Fill nulls, deduplicate species (keep most severe status), create `at_risk` flag, merge datasets |
| 3. Conservation Risk by Category | At-risk rates per category, chi-square test, Cramér's V effect size |
| 4. At-Risk Distribution Across Parks | Park-level observation share by conservation status |
| 5. What's Driving the Chi-Square? | Standardised residuals heatmap — which categories drive the signal |
| 6. Severity Breakdown | Endangered / Threatened / In Recovery / Species of Concern per category |
| 7. The 15 Endangered Species | Named list + park-level observation heatmap |
| 8. Category Risk per Park | At-risk % by category × park — tests whether parks differ in composition |
| 9. Conclusions | Summary of findings and limitations |

---

## Limitations

- Survey effort per park is not documented — cross-park observation count comparisons may reflect monitoring intensity rather than true abundance
- Conservation listings reflect human monitoring capacity; under-studied groups (plants, invertebrates) are likely under-represented
- Dataset covers 4 parks only — findings may not generalise to the US national park system broadly
