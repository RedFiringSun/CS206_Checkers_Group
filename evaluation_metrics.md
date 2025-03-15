# Fact Verification System - Evaluation Metrics

## Overview
This document analyzes the results of running the fact verification system across 5 distinct domains with 5 claims each (25 total claims).

## Domain Performance Analysis

| Domain | Avg Score | Median | Std Dev | High Confidence | Medium Confidence | Low Confidence |
|--------|-----------|--------|---------|-----------------|-------------------|----------------|
| Science & Technology | 0.7061 | 0.7216 | 0.1105 | 20.0% | 60.0% | 20.0% |
| History & Politics | 0.6376 | 0.6637 | 0.1180 | 0.0% | 60.0% | 40.0% |
| Medicine & Health | 0.8483 | 0.8783 | 0.0629 | 80.0% | 20.0% | 0.0% |
| Environmental Science | 0.8252 | 0.8592 | 0.0534 | 60.0% | 40.0% | 0.0% |
| Business & Economics | 0.8162 | 0.8499 | 0.0739 | 60.0% | 40.0% | 0.0% |
| **Overall** | **0.7667** | **0.7945** | **0.0837** | **44.0%** | **44.0%** | **12.0%** |

## Key Findings

1. **Domain Score Variation**: 
   - Medicine & Health claims received the highest confidence scores (avg: 0.8483)
   - History & Politics claims received the lowest confidence scores (avg: 0.6376)
   - Variance in scores was highest in History & Politics (std dev: 0.1180)

2. **Confidence Level Distribution**:
   - 44% of all claims had high factual confidence
   - 44% had medium factual confidence
   - 12% had low factual confidence
   - No claims received very low confidence ratings

3. **Domain-Specific Observations**:
   - Medicine & Health: 80% high confidence, suggesting robust factual verification
   - History & Politics: 40% low confidence, highest proportion of weakly verified claims
   - Environmental Science and Business & Economics: Both showed similar patterns with 60% high confidence
   - Science & Technology: Balanced distribution across confidence levels

4. **Cost Analysis**:
   - Average tokens per claim: 23.0
   - Total cost for 25 claims: $0.0028
   - Average cost per claim: $0.000112

5. **Pattern Analysis**:
   - Claims with specific numerical data (e.g., percentages, dates) tend to score higher
   - Historical claims receive lower confidence scores than contemporary facts
   - Science & Technology claims show the widest variance in scores, reflecting the diversity of topics

## Conclusion

The fact verification system demonstrates varying performance across domains, with Medicine & Health claims receiving notably higher confidence scores than History & Politics claims. This suggests the ClaimBuster API may have different verification capabilities depending on the subject matter and time period of claims.

The consistently low scores for historical claims may indicate challenges in verifying older information or the potential for historical facts to have multiple interpretations. In contrast, the higher confidence in health, environmental, and business claims suggests stronger verification capabilities for contemporary factual data, particularly when claims include specific statistics or measurable data points.

These findings highlight the importance of domain-aware fact verification and suggest future improvements could include domain-specific verification approaches or supplementary verification sources for historical claims.