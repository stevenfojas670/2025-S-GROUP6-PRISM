# 2025-S-GROUP6-PRISM

[![codecov](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM/graph/badge.svg?token=Z1QESDT3CW)](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM)

## Project Overview

PRISM is our university’s academic integrity toolkit. It ingests student submissions (from Canvas, CodeGrade, etc.), computes pairwise similarity scores via MOSS, and then applies unsupervised K-Means clustering (with PCA for visualization) to flag potentially anomalous or cheating behavior. Our pipeline generates per-pair profiles—tracking z-scores, flag counts, and mean similarity—to help TAs and professors spot outliers without needing direct access to raw grades.
