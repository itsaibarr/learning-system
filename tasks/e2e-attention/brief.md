# Research brief: Attention Is All You Need

Goal: understand how the Transformer works, what it changed, and when to use it, from the ideas, without reading the paper line by line
Domain: machine_learning
Date: 2026-10-15

## Concepts
| Id | Concept | Builds on | Sources | Unit |
| --- | --- | --- | --- | --- |
| step-by-step | Why reading one word at a time is slow | - | S1, S3 | attention-replaces-recurrence |
| attention-lookup | Attention as a weighted lookup | step-by-step | S1, S2 | attention-replaces-recurrence |
| scaled-dot | Scaled dot-product attention | attention-lookup | S1 | attention-replaces-recurrence |
| multi-head | Several attention heads at once | scaled-dot | S1 | the-transformer |
| stack-and-order | The stack and how it knows word order | multi-head | S1 | the-transformer |
| evidence | What the experiments show | stack-and-order | S1 | the-transformer |

## Definitions
- **attention function**: a mapping from a query and a set of key-value pairs to an output; the output is a weighted sum of the values, and each weight comes from how well the query matches the corresponding key [S1]
- **self-attention**: an attention mechanism that relates different positions of a single sequence to compute a representation of that sequence [S1]
- **Transformer**: a model architecture that drops recurrence and relies entirely on attention to draw global dependencies between input and output [S1]
- **fixed-length vector bottleneck**: in a basic encoder-decoder, the encoder squeezes the whole source sentence into one fixed-length vector from which the decoder generates the translation [S2]

## Misconceptions
- Attention was invented in this paper -> attention was already used on top of recurrent networks; this paper removes the recurrence [S1][S2]
- Self-attention is always cheaper than recurrence -> a layer costs O(n^2 * d) against O(n * d^2) for a recurrent layer, so it is cheaper only when the sequence length n is smaller than the dimension d; its advantage is O(1) sequential operations [S1]
- More attention heads is always better -> one head was 0.9 BLEU worse than the best setting, but quality also dropped with too many heads [S1]

## Worked examples
- step-by-step: a 30-word sentence needs 30 sequential steps in a recurrent layer, while a self-attention layer connects any two words in a constant number of operations (Table 1: O(n) against O(1)) [S1]
- scaled-dot: with d_k = 64, the dot product of two random vectors with unit variance has variance 64, so each score is divided by the square root of 64, which is 8, before the softmax [S1]
- multi-head: the model uses h = 8 heads, each with d_k = d_v = 512 / 8 = 64, so the total cost is close to one head of full size [S1]

## Sources
| Id | Source | Type | Reliability | Supports | Retrieved |
| --- | --- | --- | --- | --- | --- |
| S1 | Vaswani et al., Attention Is All You Need, https://arxiv.org/abs/1706.03762 | primary | high | the method, tables 1-4, author contributions | 2026-10-15 |
| S2 | Bahdanau, Cho, Bengio, Neural Machine Translation by Jointly Learning to Align and Translate, https://arxiv.org/abs/1409.0473 | primary | high | attention on top of recurrent encoder-decoders; the fixed-length vector bottleneck | 2026-10-15 |
| S3 | Sutskever, Vinyals, Le, Sequence to Sequence Learning with Neural Networks, https://arxiv.org/abs/1409.3215 | primary | high | the recurrent encoder-decoder the Transformer replaces | 2026-10-15 |

## Open questions
- The abstract and Table 2 give 41.8 BLEU for English-to-French, while the results text says 41.0. The paper does not explain the difference.
- Figures and the attention-visualization images were not inspected, only their captions.
- The paper's tables report translation and parsing only. Whether the gain holds on other tasks is outside what it shows.

## Access
Fidelity: full
Not read: the figures and attention-visualization images (captions only); the content of the cited references beyond S2 and S3 abstracts

## Claims
| Id | Claim | Type | Source |
| --- | --- | --- | --- |
| C1 | The Transformer is the first transduction model that relies entirely on self-attention, with no recurrence or convolution | author-claim | S1 |
| C2 | Self-attention connects all positions with a constant number of sequential operations, where a recurrent layer needs O(n) | author-claim | S1 |
| C3 | The big model reaches 28.4 BLEU on English-to-German, over 2 BLEU above the best earlier results including ensembles, after 3.5 days on 8 GPUs | evidence | S1 |
| C4 | The base model scores 27.3 BLEU on English-to-German at 3.3e18 training FLOPs, against 26.30 at 1.8e20 for the GNMT + RL ensemble | evidence | S1 |
| C5 | A single head is 0.9 BLEU worse than the best head setting, and too many heads also lowers quality | evidence | S1 |
| C6 | With 4 layers the model reaches 91.3 F1 on WSJ constituency parsing trained on WSJ only, and 92.7 semi-supervised | evidence | S1 |
| C7 | The English-to-French headline (41.8 in the abstract and table, 41.0 in the text) is stated two ways, so read it as roughly 41 to 42 until the authors clarify | interpretation | S1 |
| C8 | The evidence covers translation and parsing; it does not show the design wins on every task, which the authors also treat as future work | interpretation | S1 |

## Authors
| Author | Affiliation | Role in this paper | Source |
| --- | --- | --- | --- |
| Ashish Vaswani | Google Brain | with Illia Polosukhin, designed and implemented the first Transformer models | S1 |
| Noam Shazeer | Google Brain | proposed scaled dot-product attention, multi-head attention and the parameter-free position representation | S1 |
| Niki Parmar | Google Research | designed, implemented, tuned and evaluated many model variants | S1 |
| Jakob Uszkoreit | Google Research | proposed replacing RNNs with self-attention and started the effort to evaluate it | S1 |
| Llion Jones | Google Research | tried new model variants, wrote the first codebase, efficient inference and visualizations | S1 |
| Aidan N. Gomez | University of Toronto (work done while at Google Brain) | implemented parts of tensor2tensor | S1 |
| Lukasz Kaiser | Google Brain | designed and implemented parts of tensor2tensor | S1 |
| Illia Polosukhin | work done while at Google Research | with Ashish Vaswani, designed and implemented the first Transformer models | S1 |

## Novelty
- Existed: attention on top of recurrent encoder-decoders, which soft-searches the source words for each output word [S2]; recurrent encoder-decoders that pass one fixed-length vector [S3]; convolutional models that compute positions in parallel [S1]
- Changed: removed recurrence and convolution entirely; scaled the dot products by 1/sqrt(d_k); ran several attention heads in parallel; added sine and cosine position signals [S1]
- Shown: attention alone reaches state-of-the-art translation quality at a fraction of the training cost, and carries over to constituency parsing [S1]
