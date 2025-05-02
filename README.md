# 2025-S-GROUP6-PRISM

| Branch      | Coverage                                |
| ----------- | --------------------------------------- |
| **main**    | [![cov-main](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM/graph/badge.svg?token=Z1QESDT3CW)](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM) |
| **dev**     | [![cov-dev](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM/graph/badge.svg?branch=dev&token=Z1QESDT3CW)](https://codecov.io/gh/donessie94/2025-S-GROUP6-PRISM?branch=dev) |

PRISM: Academic Integrity Toolkit

PRISM (Pairwise Risk Identification & Similarity Metrics) is an automated academic integrity pipeline designed for universities. PRISM ingests student submissions from platforms like Canvas and CodeGrade, computes similarity scores using MOSS, and applies unsupervised machine learning (K-Means clustering combined with PCA for visualization) to detect anomalous behavior indicative of cheating.

Our toolkit produces clear analytics visualizations and statistical insights, helping instructors and teaching assistants proactively identify potential integrity violations—without directly accessing raw student grades.

⸻

Table of Contents
	1.	Overview
	2.	Key Features
	3.	Visualizations
	4.	Tech Stack

⸻

Overview

PRISM streamlines academic integrity checks by automating pairwise analysis of student submissions, generating insightful visualizations, and clearly highlighting outliers based on z-scores and similarity metrics.

⸻

Key Features
	•	Automated Data Ingestion: Extract and process assignment data from Canvas and CodeGrade seamlessly.
	•	Similarity Analysis: Leverage MOSS to compute pairwise submission similarity.
	•	Statistical Detection: Utilize statistical techniques (z-scores, percentiles) to flag outlier pairs.
	•	Machine Learning Clustering: Apply K-Means clustering with PCA dimensionality reduction for effective outlier detection.
	•	Interactive Visualizations: Generate easy-to-interpret plots to communicate results clearly.

⸻

Visualizations

Pairwise Clustering Visualization

<img width="1291" alt="Screenshot 2025-05-02 at 11 54 21 AM" src="https://github.com/user-attachments/assets/64b812cd-e97d-4636-8808-2e8265e255ae" />

	•	Filename: student_pair_clusters.png
	•	Description:
This scatter plot shows clusters of student pairs based on nine distinct features, including similarity metrics and statistical outliers. The most-suspicious cluster (highest mean z-score) is clearly highlighted in red. A detailed sidebar lists the top 20 suspicious pairs identified by maximum z-scores.

Statistical Analytics Dashboard
<img width="1308" alt="Screenshot 2025-05-02 at 11 55 10 AM" src="https://github.com/user-attachments/assets/e6e5e4cb-8a19-4bcd-8852-18ca36cca944" />

	•	Filename: statistical_dashboard.png
	•	Description:
Provides a comprehensive statistical overview including:
	•	Mean Similarity Histogram: Displays distribution of similarity scores against an expected normal distribution.
	•	Outlier Detection Pie Chart: Shows the percentage of normal vs. outlier (flagged) pairs.
	•	Q-Q Plot: Assesses the normality of similarity scores.
	•	Fraction of Pairs ≥ Z: Demonstrates the cumulative fraction of pairs exceeding specific z-scores.

Tech Stack
	•	Backend: Python, Django, Django Rest Framework
	•	Database: PostgreSQL
	•	Analysis: pandas, NumPy, scipy, scikit-learn
	•	Visualization: matplotlib, seaborn
	•	Similarity Detection: MOSS
	•	CI/CD & Deployment: GitHub Actions, Docker
