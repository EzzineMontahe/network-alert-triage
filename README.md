# Network Alert Triage

Machine learning detector for network attacks, with an LLM agent that explains each alert. Runs locally.

**Status: in progress.** The detector experiments are done. The agent and dashboard are being built.

## What exists so far
- Cleaned the CIC-IDS2017 Friday PortScan file: 286,096 flows, 78 features
- Random Forest on an 80/20 split: 5 mistakes out of 57,220 test flows
- Removing the destination port feature did not change the result
- Isolation Forest (no labels, trained on normal traffic only): caught 0 port scans, AUC 0.56
- Finding: individual port scan flows look like normal traffic, so a per-flow anomaly detector cannot catch them. A scan is a pattern across many flows.
- On DDoS, an attack it never studied: Random Forest caught 58% with 0 false alarms, Isolation Forest caught 17% with 9.5% false alarms
- Test on a realistic mix of mostly normal traffic

## Limits
- This file is balanced (55% attacks), which is not realistic. A near-perfect score here does not prove the detector works on a real network.

## Roadmap
- [x] Data cleaning and exploration
- [x] Random Forest and Isolation Forest experiments
- [x] Test on an attack the model has never seen (DDoS)
- [x] Test on a realistic mix of mostly normal traffic
- [ ] Capture and test on traffic from my own lab
- [ ] Agent that sends each alert to an LLM for severity, explanation and next step
- [ ] Dashboard
- [ ] Docker Compose setup

## Dataset
CIC-IDS2017, Canadian Institute for Cybersecurity, University of New Brunswick. The data is not included in this repository.

## Stack
Python, pandas, scikit-learn, Jupyter
