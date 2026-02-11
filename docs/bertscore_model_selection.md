### Level 3.2 — Model Selection for Semantic Consistency (BERTScore)

**BERTScore** (Zhang et al., 2020) is a reference-based evaluation metric that leverages contextual embeddings from pre-trained language models to compute token-level cosine similarities between candidate and reference texts. Unlike n-gram-based metrics such as BLEU or ROUGE, BERTScore captures semantic equivalence even when different surface forms are used — a critical property for evaluating therapeutic language, where clinically equivalent responses may differ substantially in wording.

The metric computes precision, recall, and F1 by greedily matching each token in the candidate to the most similar token in the reference using cosine similarity over contextual embeddings. For this study, the **mean pairwise F1** across all $\binom{n}{2}$ trial pairs serves as the primary measure of output consistency (termed *Execution Fidelity*).

#### Candidate Models

The BERTScore library supports over 130 embedding models. Four candidates were evaluated for this study:

| Model | Parameters | Best Layer | WMT16 Pearson $r$ | Rank |
|-------|-----------|------------|-------------------|------|
| `roberta-large` | 355M | 17 | 0.7386 | 20 |
| `roberta-large-mnli` | 355M | 19 | 0.7536 | 6 |
| `microsoft/deberta-large-mnli` | 304M | 18 | 0.7736 | 3 |
| `microsoft/deberta-xlarge-mnli` | 750M | 18 | 0.7781 | 1 |

*Pearson correlations with human judgments on the WMT16 to-English evaluation dataset (Zhang et al., 2020; Tiiiger/bert_score model spreadsheet).*

#### Considered Alternative: `roberta-large` (Default)

`roberta-large` is the BERTScore default and the most widely cited model in published work using BERTScore. Initial implementation used this model. The following arguments were considered in its favor:

- **Comparability** with existing literature reporting BERTScore values.
- **No workaround needed** — runs out of the box without configuration patches.
- **Computational efficiency** — 355M parameters vs. 750M for DeBERTa-XLarge.

These arguments were ultimately judged insufficient for this use case (see below).

#### Design Decision: `microsoft/deberta-xlarge-mnli`

This study adopts **`microsoft/deberta-xlarge-mnli`** (He et al., 2021), layer 18, as the embedding model for the following reasons:

1. **NLI fine-tuning matches the evaluation task.** DeBERTa-XLarge-MNLI is fine-tuned on the Multi-Genre Natural Language Inference corpus (Williams et al., 2018), where the objective is to determine whether one sentence entails, contradicts, or is neutral to another. This is functionally identical to Level 3.2's measurement task: determining whether two therapist responses convey the same therapeutic intervention. A model trained to compare sentence-level meaning produces more semantically grounded embeddings for pairwise similarity than one trained only on masked language modeling.

2. **Better signal-to-noise ratio for therapeutic text.** Therapy responses that are clinically equivalent may differ substantially in surface form (e.g., *"Let's modify the ending of your dream"* vs. *"I'd like us to rescript your nightmare so it feels safe"*). DeBERTa's disentangled attention mechanism — which separately encodes content and positional information — combined with NLI training yields embeddings that better distinguish genuine semantic divergence from mere lexical variation. This means BERTScore F1 drops reflect actual changes in therapeutic content, not surface-level rephrasing.

3. **Highest correlation with human judgments.** Ranked #1 out of 130+ supported models with $r = 0.778$ on WMT16, compared to $r = 0.739$ for `roberta-large` (rank 20). The gap ($\Delta r = 0.04$) represents the difference between the best available model and a mid-tier option, not a marginal improvement.

4. **Cross-paper comparability is limited regardless.** Absolute BERTScore values depend on text domain, response length, and language. Direct comparison of F1 values across studies using different corpora is unreliable whether using RoBERTa or DeBERTa. The methodological soundness of the model choice matters more than matching other papers' defaults.

5. **Tokenizer overflow is a trivial, well-documented fix.** Both DeBERTa variants expose `model_max_length ≈ 10^{30}` in the HuggingFace tokenizer configuration, causing an `OverflowError` in the Rust backend on Python 3.10+. The fix is a single line (`model_max_length = 512`) applied via `BERTScorer`, consistent with the documented 510-token truncation limit that applies to all BERTScore models. This does not introduce fragility — it corrects a misconfigured default in the model card.

#### References

- Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). BERTScore: Evaluating Text Generation with BERT. *International Conference on Learning Representations (ICLR)*. https://openreview.net/forum?id=SkeHuCVFDr
- He, P., Liu, X., Gao, J., & Chen, W. (2021). DeBERTa: Decoding-enhanced BERT with Disentangled Attention. *International Conference on Learning Representations (ICLR)*. https://openreview.net/forum?id=XPZIaotutsD
- Liu, Y., Ott, M., Goyal, N., Du, J., Joshi, M., Chen, D., Levy, O., Lewis, M., Zettlemoyer, L., & Stoyanov, V. (2019). RoBERTa: A Robustly Optimized BERT Pretraining Approach. *arXiv:1907.11692*.
- Williams, A., Nangia, N., & Bowman, S. (2018). A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference. *NAACL-HLT*. https://aclanthology.org/N18-1101/
- BERTScore model correlations spreadsheet: https://docs.google.com/spreadsheets/d/1RKOVpselB98Nnh_EOC4A2BYn8_201tmPODpNWu4w7xI
