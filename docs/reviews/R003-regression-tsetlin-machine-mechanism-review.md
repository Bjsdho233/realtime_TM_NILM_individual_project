# R003 — Regression Tsetlin Machine Mechanism Review

**Status:** Complete — literature and pinned-source review; successor checks not executed\
**Owner:** Tianhang Tan\
**Created:** 2026-07-24\
**Track:** R-series review\
**Reviewed scope:** vanilla Regression Tsetlin Machine (rTM), integer-weighted
rTM, C-RTM mechanism evidence, one energy-forecasting application, the original
rTM reference implementation, the implementation immediately preceding the
integer-weighted paper, and TMU `v0.8.3`\
**Sources/revisions:** four supplied PDFs; `cair/regression-tsetlin-machine`
commit `f65f8a093f474bdfaa3b019450318fe960b522f5`;
`cair/pyTsetlinMachine` commit
`079a09327b4d566d2f27b66db9b5893493c0e549`; `cair/tmu` tag `v0.8.3`,
commit `df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483`

## Review question

What do the reviewed papers and fixed public implementations actually establish
about rTM representation, learning, parameters, integer weights, continuous
input handling, and output scaling; which of those facts can guide a possible
NILM implementation; and which conclusions must remain hypotheses until local
source parity and controlled mechanism experiments are completed?

## Claim boundary

This document is a read-only mechanism and evidence review. No TM was trained,
no REDD data or sealed Protocol R candidate-test block was accessed, and no new
model result was created. It does not:

- replace the current formal event-level binary-TM baseline;
- approve rTM, weighted rTM, or a classification-TM–rTM gate as the project
  method;
- select a target range, Booleanisation, causal window, clipping policy,
  hyperparameter range, or evaluation metric;
- establish that the source installed on Tianhang's computer is byte-identical
  to the public TMU `v0.8.3` tag;
- claim that an rTM path can reuse the current classifier export or Pico
  implementation without additional work.

Later source checks and experiments should be recorded in their own authorised
T-series or E-series evidence. This review can then be revised with dated
evidence links rather than silently converting present hypotheses into facts.

## 1. How evidence is labelled

The report uses five labels to prevent literature claims, code behaviour, and
project ideas from being mixed together.

| Label | Meaning |
|---|---|
| **Paper definition** | Stated in a reviewed paper, with section, equation, table, or page locator |
| **Pinned-source observation** | Read directly from a named repository path at a fixed commit or tag |
| **Mechanism inference** | Follows from a stated equation or inspected control flow, but was not itself measured here |
| **NILM hypothesis** | Plausible project-specific expectation that can be accepted or rejected only by experiment |
| **Open item** | Ambiguous, internally inconsistent, version-dependent, or not yet inspected locally |

The notation in this report is kept consistent even where a paper uses a
different convention:

- \(X\): Boolean input vector;
- \(C_j(X)\in\{0,1\}\): output of clause \(j\);
- \(m\): number of clauses;
- \(T\): rTM output scale or nominal resolution parameter;
- \(y\): target value;
- \(\hat y\): predicted value;
- \(w_j\): integer weight of clause \(j\);
- \(V(X)\): raw sum of active clause contributions.

## 2. Terminology that must not be conflated

| Term | Meaning in this project or source |
|---|---|
| **cTM** | Classification Tsetlin Machine. In the possible `cTM–rTM` design, this would estimate appliance state or act as a gate. |
| **rTM / RTM** | Regression Tsetlin Machine. Here the leading `r` means regression, not real-time. |
| **RTM-IW / weighted rTM** | rTM whose clauses carry learned integer weights. |
| **C-RTM** | *Convolutional Regression Tsetlin Machine*, an image-oriented model in the 2021 paper. It is not the project's classification gate. |
| **TMU** | Tsetlin Machine Unified, the software toolbox considered as a PC-side experimental implementation and possible golden reference. It is not an embedded rTM core by itself. |

## 3. Evidence inspected

### 3.1 Papers

| ID | Source and exact role | Main locators | Supplied review file and SHA-256 |
|---|---|---|---|
| **P1** | K. D. Abeyrathna et al., *The Regression Tsetlin Machine: A Novel Approach to Interpretable Nonlinear Regression*, *Philosophical Transactions of the Royal Society A*, vol. 378, issue 2164, 2020, article 20190165. This is the principal vanilla-rTM source. [DOI](https://doi.org/10.1098/rsta.2019.0165) | §3 continuous input; §4 equations (4.1)–(4.3); §5 figures 5–7 and tables 2–3; PDF pp. 6–13 | `rsta.2019.0165.pdf`; `f5e4ee6c8bd83832b8db8c7f5339dc11af9556ae812fb990b29d324d188ea76e` |
| **P2** | K. D. Abeyrathna, O.-C. Granmo, and M. Goodwin, *A Regression Tsetlin Machine with Integer Weighted Clauses for Compact Pattern Representation*, arXiv:2002.01245v1, 2020. This reviewed preprint is the principal RTM-IW source. [arXiv](https://arxiv.org/abs/2002.01245) | §2 equations (1)–(5); §4 equation (8) and Algorithm 1; §5 tables 1–2 and figure 4; PDF pp. 2–11 | `2002.01245v1.pdf`; `525076aa775f2d277f1a8d39ef0b322a378c7564583f733e02f85c8f2e01eb67` |
| **P3** | K. D. Abeyrathna, O.-C. Granmo, and M. Goodwin, *Convolutional Regression Tsetlin Machine: An Interpretable Approach to Convolutional Regression*, ICMLT 2021. This is supporting evidence for additive clauses and duplicate-clause allocation, not a direct time-series method. [DOI](https://doi.org/10.1145/3468891.3468901) | §3 equations (4)–(6); §4 tables 2–7; PDF pp. 4–8 | `3468891.3468901.pdf`; `1f0e827f02357d39d8e3e1eb6a6894731a156330fe87bcda979ac742fca6ba05` |
| **P4** | S. N. Ranasinghe and H. S. G. Pussewalage, *Short-term Energy Forecasting using the Regression Tsetlin Machine*, UCC 2023. This establishes an energy-domain use case, but not NILM. [DOI](https://doi.org/10.1145/3603166.3632543) | §4 data and features; §5 split and results; tables 1–3; PDF pp. 2–4 | `3603166.3632543.pdf`; `701e56fbb317d3a99943ab2a74aa8b479e5496bb2cd9c97e587bd239ebb19c8d` |

P1 is preferred over the shorter 2019 conference paper when describing the
vanilla mechanism because it includes continuous-input preprocessing, the full
feedback description, and real-data experiments. The formal journal issue is
dated 2020; the DOI/article identifier and the supplied PDF's citation line
contain 2019, so those two dates should not be silently treated as contradictory
papers.

The supplied P2 text is specifically arXiv v1. A later conference chapter is
published as *Integer Weighted Regression Tsetlin Machines* under
[DOI 10.1007/978-3-030-55789-8_59](https://doi.org/10.1007/978-3-030-55789-8_59).
This review does not assume that every line, figure, or setting in the supplied
preprint is identical to that final chapter. P2, P3, and P4 add evidence but do
not replace P1's definition.

### 3.2 Public source code

| ID | Fixed source | Paths used in this review | Evidential role |
|---|---|---|---|
| **C1** | [`cair/regression-tsetlin-machine@f65f8a0`](https://github.com/cair/regression-tsetlin-machine/tree/f65f8a093f474bdfaa3b019450318fe960b522f5) | [`RegressionTsetlinMachine.pyx`](https://github.com/cair/regression-tsetlin-machine/blob/f65f8a093f474bdfaa3b019450318fe960b522f5/RegressionTsetlinMachine.pyx), [`ArtificialDataDemo.py`](https://github.com/cair/regression-tsetlin-machine/blob/f65f8a093f474bdfaa3b019450318fe960b522f5/ArtificialDataDemo.py) | Original unweighted reference implementation linked by P1 |
| **C2** | [`cair/pyTsetlinMachine@079a093`](https://github.com/cair/pyTsetlinMachine/tree/079a09327b4d566d2f27b66db9b5893493c0e549) dated 2020-01-21 | [`pyTsetlinMachine/tm.py`](https://github.com/cair/pyTsetlinMachine/blob/079a09327b4d566d2f27b66db9b5893493c0e549/pyTsetlinMachine/tm.py), [`pyTsetlinMachine/ConvolutionalTsetlinMachine.c`](https://github.com/cair/pyTsetlinMachine/blob/079a09327b4d566d2f27b66db9b5893493c0e549/pyTsetlinMachine/ConvolutionalTsetlinMachine.c) | Contemporaneous author-repository snapshot immediately preceding P2; useful for identifying possible paper/code divergence, but not explicitly identified by P2 as its experiment artifact |
| **C3** | [`cair/tmu@v0.8.3`](https://github.com/cair/tmu/tree/df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483), commit `df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483` | [`vanilla_regressor.py`](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py), [`weight_bank.py`](https://github.com/cair/tmu/blob/v0.8.3/tmu/weight_bank/weight_bank.py), [`WeightBank.c`](https://github.com/cair/tmu/blob/v0.8.3/tmu/lib/src/WeightBank.c), [`ClauseBank.c`](https://github.com/cair/tmu/blob/v0.8.3/tmu/lib/src/ClauseBank.c), [`base.py`](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/base.py), [`StandardBinarizer`](https://github.com/cair/tmu/blob/v0.8.3/tmu/preprocessing/standard_binarizer/binarizer.py), [`RegressionDemo.py`](https://github.com/cair/tmu/blob/v0.8.3/examples/regression/RegressionDemo.py) | Intended project-side implementation reference |

P4 links only to the moving `cair/pyTsetlinMachine` repository and gives no
commit. Therefore, its reported result cannot be tied safely to C2, C3, or the
current repository head. That missing version identity is part of P4's
reproducibility limitation.

## 4. Main conclusion

rTM is best understood as a **quantised additive rule regressor**:

1. Boolean clauses identify patterns.
2. Each active unit-weight clause contributes one vote.
3. The vote sum is mapped to the target scale.
4. Underprediction invokes Type I feedback to make suitable clauses activate
   more often; overprediction invokes Type II feedback to suppress unsuitable
   activations.
5. Integer-weighted rTM lets one pattern contribute several vote units without
   requiring the same pattern to be represented by the same number of separate
   clauses.

This is different from assigning a class ID to a power level and different from
gradient-based continuous regression. For a fixed trained model, its output lies
on a discrete lattice. The word “regression” means that the model is trained
against an ordered numerical target; it does not mean that every real number is
reachable.

The reviewed evidence supports the mechanism and shows that rTM can work on
small artificial problems and several tabular regression tasks. It does **not**
establish that rTM is suitable for causal NILM, that weighted clauses reduce
actual embedded cost, or that a classification gate improves rTM. Those are
well-motivated but still testable project hypotheses.

The largest practical finding is that there is no single implementation-neutral
“standard rTM” behaviour. P1, P2, C1, C2, and TMU `v0.8.3` differ in target
mapping, feedback probability, clipping, weight initialisation, weight lower
bound, and random-update coupling. Later code and dissertation text must name
the exact implementation instead of attributing all observed behaviour to rTM
in general.

## 5. Vanilla rTM mechanism

### 5.1 Boolean clauses remain the basic pattern unit

Given Boolean variables and their negations,

\[
L=[x_1,\ldots,x_o,\neg x_1,\ldots,\neg x_o],
\]

clause \(j\) is a conjunction of the literals selected by its Tsetlin Automata:

\[
C_j(X)=\bigwedge_{k\in I_j} l_k.
\]

The clause produces one only when every included literal is satisfied. The TA
states determine whether each literal is included or excluded. P1 §2 and P2 §2
retain the standard Type Ia, Type Ib, and Type II roles:

- Type Ia reinforces literals associated with a currently successful active
  clause;
- Type Ib encourages exclusion and reduces over-specific or unsuitable clause
  composition;
- Type II attempts to make a currently active false-positive clause output zero
  by including a literal that is zero for the current input.

The rTM change is mainly at the aggregation and feedback-selection level. The
Boolean clause is not replaced by a numerical leaf or neuron.

### 5.2 Continuous inputs must first become Boolean

**Paper definition.** P1 §3 uses every distinct training value of a continuous
feature as a threshold. For thresholds \(v_1<\cdots<v_q\), it defines bits
equivalent to:

\[
b_i(x)=\mathbb{1}[x\leq v_i].
\]

For the paper's example \(x=5.779\) and thresholds
\((3.834,5.779,10.008)\), the code is \((0,1,1)\). The cumulative structure
preserves order relative to known thresholds. Combined with negated literals,
clauses can express intervals such as:

\[
x>100 \land x\leq300.
\]

The paper calls this representation lossless. The claim needs a precise
boundary:

- it can distinguish the distinct values represented by its complete threshold
  set;
- unseen values that fall between the same adjacent thresholds receive the same
  code;
- one threshold per unique value can be prohibitively large for long power time
  series;
- thresholds must be fitted on training data only in this project.

**Pinned-source observation.** TMU `v0.8.3`
[`StandardBinarizer.fit`](https://github.com/cair/tmu/blob/v0.8.3/tmu/preprocessing/standard_binarizer/binarizer.py#L23-L42)
excludes the smallest unique value, limits the retained values with
`max_bits_per_feature`, and samples approximately uniformly along the sorted
unique-value list. Its
[`transform`](https://github.com/cair/tmu/blob/v0.8.3/tmu/preprocessing/standard_binarizer/binarizer.py#L44-L53)
uses \(\mathbb{1}[x\geq v_i]\), the opposite bit orientation to P1. With both
literal polarities available, the two orientations can represent the same
threshold relations in principle, but their bit meanings and learning dynamics
must not be treated as identical without a check.

TMU's
[`RegressionDemo.py`](https://github.com/cair/tmu/blob/v0.8.3/examples/regression/RegressionDemo.py#L22-L47)
fits the binarizer to the full dataset before the train/test split. That script
is a usage demonstration, not an acceptable Protocol R experiment template.
Project code must split first, fit thresholds on training data, and reuse the
frozen thresholds for validation, test, replay, host-native inference, and Pico
inference.

### 5.3 Positive-target output in the paper

P1 §4 removes clause polarity for the positive-output case and treats all clauses
as additive components:

\[
\hat y_{\mathrm{P1}}(X)
=
\frac{\sum_{j=1}^{m}C_j(X)}{T}\,y_{\max}.
\tag{1}
\]

P1 calls \(T\) the output resolution and explicitly states that \(y_{\max}\) is
a scaling reference, not necessarily a hard output upper bound. The smallest
unit-vote change in this mapping is:

\[
\Delta y_{\text{unit}}=\frac{y_{\max}}{T}.
\tag{2}
\]

If \(m>T\), the unbounded paper equation can exceed \(y_{\max}\). If
unit-weight clauses are used and \(m<T\), the largest reachable vote sum is
\(m\), so the model cannot reach the reference maximum. Thus \(m\geq T\) is a
coverage condition for that particular mapping, not a guarantee of good
regression.

P1's Figure 3 shows a conceptual range from \(y_{\min}\) to \(y_{\max}\), but
equation (4.1) only specifies the positive-target \(y_{\max}\) form. A footnote
says negative outputs can be supported with negative-polarity clauses. P1 does
not provide the later implementation's explicit min–max affine formula.
Accordingly, equation (1), a min–max implementation, and a negative-target
extension must be described separately.

### 5.4 Feedback direction

P1 gives:

\[
\text{Feedback}=
\begin{cases}
\text{Type I}, & \hat y<y,\\
\text{Type II}, & \hat y>y.
\end{cases}
\tag{3}
\]

The direction is intuitive:

- when the estimate is too low, increase the number of appropriate active
  clause contributions;
- when the estimate is too high, reduce inappropriate active contributions.

No feedback is selected by equation (3) when prediction and target are equal.
However, this does not imply that OFF samples generally receive no feedback:
they receive none only when their actual prediction also equals the OFF target.

### 5.5 Feedback probability is source-dependent

There is no safe universal probability formula across the reviewed sources.

**P1 paper definition:**

\[
P_{\mathrm{act}}
=K\frac{|\hat y-y|}{y_{\max}},
\tag{4}
\]

where \(K\) is said to adjust the activation probability to the clause count.
The paper does not give a general closed-form rule for choosing \(K\).

**P2 restatement:**

\[
P(p_j=1)=\frac{|\hat y-y|}{T},
\tag{5}
\]

within P2's normalised-output description. Its notation and later artificial
targets are not completely consistent, so equation (5) should be cited as P2's
formulation rather than merged with equation (4).

**C1 original code:** the Bernoulli probability is linear absolute error divided
by the fitted target range:

\[
p_{\mathrm{C1}}
=\frac{|\hat y-y|}{y_{\max}-y_{\min}}.
\tag{6}
\]

See
[`RegressionTsetlinMachine.pyx` lines 192–202](https://github.com/cair/regression-tsetlin-machine/blob/f65f8a093f474bdfaa3b019450318fe960b522f5/RegressionTsetlinMachine.pyx#L192-L202).

**TMU `v0.8.3` pinned-source observation:** after target encoding and training
vote clipping, the probability is the squared normalised encoded error:

\[
p_{\mathrm{TMU}}
=
\left(\frac{\tilde V-z}{T}\right)^2.
\tag{7}
\]

See
[`vanilla_regressor.py` lines 123–128](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L123-L128).

These differences change the learning dynamics, especially near small errors.
They are not cosmetic variations in notation.

### 5.6 The role of \(s\)

In P2 §2, Type Ia reinforces matching literals in an active clause, while Type
Ib is selected with probability \(1/s\). In standard TM terms, \(s\) influences
the balance between detailed/specific clauses and broader patterns. Increasing
\(s\) commonly favours more specific clauses, but it is not an independent
“accuracy control”, and its effect depends on the data, literals, clause budget,
and implementation.

For a causal NILM window, a high \(s\) could encourage rules tied to many exact
threshold/time-position conditions; that could help distinguish events or could
overfit house-specific patterns. This is a NILM hypothesis, not a direction that
can be selected from the literature alone.

### 5.7 rTM has no recurrent memory in the reviewed formulation

The inspected prediction functions evaluate a fixed input \(X\), compute clause
outputs, and sum them. There is no recurrent hidden state that carries appliance
history between samples. P4 therefore supplies calendar fields and past-week
consumption explicitly as input features.

For causal NILM, temporal information must similarly come from a declared input
representation, for example:

\[
[P_{t-L+1},\ldots,P_t]\longrightarrow
\text{Boolean features}\longrightarrow\hat P^{(a)}_t,
\]

or from separately defined external state logic. Window length, sampling rate,
event alignment, boundary reset, and decision delay remain experimental design
choices.

## 6. Parameter relationships

| Parameter or artefact | Supported role | Important coupling or limitation | Current project status |
|---|---|---|---|
| \(m\), number of clauses | Number of learned Boolean pattern components | In unit-weight rTM it also limits maximum vote count; in weighted rTM it still limits pattern diversity but not weight magnitude | Must be varied jointly with \(T\), representation size, and cost |
| \(T\) | Denominator/output scale; nominal unit-vote spacing; part of feedback scaling in P2 and TMU | Does not by itself determine accuracy; interacts with target range, \(m\), weights, error probability, and integer target encoding | No fixed NILM value |
| \(s\) | Type I specificity balance | Interacts with feature count, threshold density, causal-window length, and clause count | No fixed direction |
| TA states / `number_of_state_bits_ta` | Persistence and update depth of literal include/exclude decisions | Affects learning dynamics and memory; it is separate from output resolution | TMU behaviour requires a mechanism check before tuning |
| Boolean thresholds | Determine information retained and literal count | More bits may improve input resolution while increasing clause state and embedded cost | Fit on training only; bit budget unselected |
| Epochs | Number of passes through training data | More passes can improve learning or overfit; API meaning differs between C1 and TMU | Must be recorded explicitly |
| \(y_{\min},y_{\max}\) | Code-side target scale and inverse mapping | Outliers change nominal watt-per-vote and feedback magnitude; fitted values are learned preprocessing | Must be train-derived and serialised |
| Clause weights | Multiplicity of a learned pattern in RTM-IW | Non-negative weights cannot directly subtract power; overlapping clauses can still duplicate effects | Weighted and unweighted require controlled comparison |

The correct design process is not “choose a large \(T\) for precision and then
tune \(m\) separately”. A provisional watt-scale target implies a nominal
vote spacing; the clause and weight structure must then be able to cover the
range, and the resulting feedback frequency and resource cost must be measured.

## 7. Integer-weighted rTM

### 7.1 Representation

P2 changes the unit-vote sum to:

\[
\hat y_{\mathrm{IW}}(X)
=
\frac{1}{T}\sum_{j=1}^{m}w_j C_j(X)
\quad
\text{in P2's normalised notation},
\tag{8}
\]

with \(w_j\in\{0,1,2,\ldots\}\).

The intended interpretation is that a clause with \(w_j=N\) replaces \(N\)
unit-weight clauses that learned the same sub-pattern. For the artificial
three-bit mapping:

\[
4x_1+2x_2+x_3,
\]

vanilla rTM needs seven unit contributions:

\[
4\times(x_1)+2\times(x_2)+1\times(x_3),
\]

whereas an ideal RTM-IW representation needs three clauses with weights
\((4,2,1)\). P1 table 2 and P2 table 1 provide this explicit construction.
P3 later shows the same \(8,4,2,1\) duplication idea in a four-pattern
convolutional example.

This demonstrates **clause-count compactness for a known synthetic function**.
It does not prove lower total model bytes, RAM, inference latency, or energy on
the project's implementation. Weighted storage, integer width, clause overlap,
and export format must all be included in a real cost comparison.

### 7.2 Paper weight learning

P2 Algorithm 1 initialises:

\[
w_j(0)=0.
\]

For an underprediction, an active selected clause increases by one. For an
overprediction, a selected positive weight decreases by one. Weights cannot
become negative. The paper argues that \(w_j=0\) can disable an unwanted clause
globally.

The weight and clause structure are learned together; RTM-IW is not presented
as “train vanilla rTM first and fit weights afterwards”.

### 7.3 A real ambiguity in P2

P2 says that a weight is updated when its clause receives Type Ia or Type II
feedback. Its earlier Type II definition acts only when \(C_j(X)=1\).
However, the decrement branch in Algorithm 1 checks underprediction/selection
and \(w_j>0\) but omits \(C_j(X)=1\).

This document does not silently repair the pseudocode. The two defensible
readings are:

1. the surrounding Type II definition supplies the missing active-clause
   condition; or
2. Algorithm 1 intends to decrement any selected positive weight on an
   overprediction.

C2 and C3 implement the first behaviour, but that does not erase the ambiguity
in the paper itself.

### 7.4 What P2's experiments establish

P2 uses six artificial datasets with only two, three, or four Boolean inputs.
It shows that integer weights can represent repeated synthetic patterns with
fewer clauses and reports competitive MAE against unweighted and real-weight
variants.

Its evidence is limited:

- no real continuous-input regression dataset is used;
- actual memory, latency, and energy are not reported;
- repeated seeds and uncertainty intervals are not reported;
- the broad comparison sets \(T=m\) for vanilla rTM but \(T=100m\) for the
  weighted models, so weight use and resolution are not fully isolated;
- the “more interpretable” conclusion follows mainly from a smaller conceptual
  rule set, not a user study or complex real-data clause analysis;
- figure 4 reports that almost no clauses reach zero weight in the noiseless
  high-clause setting, while more are disabled in noisy data; zero-weight
  sparsity is therefore not automatic.

There is also an internal numerical concern. P2 figure 3 labels an unweighted
run with \(m=70\) and \(T=100000\) as reaching zero MAE. Under its own
unweighted equation, a 70-clause vote sum divided by 100000 cannot cover a
normalised target range up to one. The paper does not explain an omitted output
scale or different implementation for this figure. The setting should not be
used to derive a NILM parameter rule.

## 8. Paper–implementation comparison

### 8.1 Original unweighted reference code C1

C1 implements a min–max affine inverse mapping:

\[
\hat y_{\mathrm{C1}}
=y_{\min}
+\frac{\operatorname{clip}(V,0,T)}{T}
(y_{\max}-y_{\min}).
\tag{9}
\]

The vote sum is clipped inside
[`sum_up_clause_votes`](https://github.com/cair/regression-tsetlin-machine/blob/f65f8a093f474bdfaa3b019450318fe960b522f5/RegressionTsetlinMachine.pyx#L111-L126),
and both update and prediction call that function. Therefore C1 cannot predict
outside the fitted target range, despite P1's statement that \(y_{\max}\) is not
a hard upper bound.

C1 also differs from P1's activation equation by using the linear normalised
range error in equation (6), with no explicit \(K\). Its
[`fit`](https://github.com/cair/regression-tsetlin-machine/blob/f65f8a093f474bdfaa3b019450318fe960b522f5/RegressionTsetlinMachine.pyx#L258-L283)
accepts an `epochs` argument and performs all passes internally.

### 8.2 Contemporaneous pre-P2 implementation C2

The inspected public `pyTsetlinMachine` commit is dated approximately two weeks
before the supplied P2 preprint:

- initialises every clause weight to one;
- prevents weighted-regression decrements below one;
- uses squared encoded error \((\text{error}/T)^2\);
- selects one feedback mask and uses the same event for clause-structure and
  weight updates;
- clips the vote sum to \(T\) for both training and inference;
- min–max encodes the target to integer values in \(0\ldots T\).

These behaviours can be located in
[`ConvolutionalTsetlinMachine.c`](https://github.com/cair/pyTsetlinMachine/blob/079a09327b4d566d2f27b66db9b5893493c0e549/pyTsetlinMachine/ConvolutionalTsetlinMachine.c)
and the
[`RegressionTsetlinMachine` wrapper](https://github.com/cair/pyTsetlinMachine/blob/079a09327b4d566d2f27b66db9b5893493c0e549/pyTsetlinMachine/tm.py).

Thus the paper's zero initial/minimum weight and linear-looking \(p_j\)
pseudocode do not literally describe this contemporaneous public snapshot. P2
does not identify an exact experiment commit, so the snapshot is evidence of a
nearby implementation difference, not proof that this exact code produced P2's
tables.

### 8.3 TMU `v0.8.3` target mapping

TMU first stores the training target extrema:

\[
y_{\min}=\min(Y_{\mathrm{train}}),\qquad
y_{\max}=\max(Y_{\mathrm{train}}).
\]

It then encodes each target as:

\[
z
=
\left\lfloor
\frac{y-y_{\min}}{y_{\max}-y_{\min}}T
\right\rfloor,
\tag{10}
\]

where the floor-like behaviour comes from conversion to `np.int32` for
non-negative scaled values. See
[`vanilla_regressor.py` lines 80–95](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L80-L95).

For each training sample:

\[
V=\sum_{j=1}^{m}w_j C_j(X),
\qquad
\tilde V=\operatorname{clip}(V,0,T),
\tag{11}
\]

and equation (7) selects the magnitude of Type I or Type II updates.

At inference, however, TMU does **not** clip \(V\):

\[
\hat y_{\mathrm{TMU}}
=y_{\min}
+\frac{V}{T}(y_{\max}-y_{\min}).
\tag{12}
\]

See
[`fit` lines 120–158](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L120-L158)
and
[`predict` lines 161–170](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L161-L170).

Consequences that follow from this control flow but still require a runtime
probe are:

- predictions can exceed \(y_{\max}\) when raw inference vote \(V>T\);
- predictions cannot fall below \(y_{\min}\) while weights are non-negative;
- if a maximum-target training sample has raw \(V>T\), training sees
  \(\tilde V=T=z\) and supplies no correction, even though inference can expose
  the larger raw vote;
- changing \(y_{\min}\) or \(y_{\max}\) changes both nominal watt-per-vote and
  feedback scale.

### 8.4 TMU `v0.8.3` weighted behaviour

The regressor initialises all weights to one in
[`init_weight_bank`](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L75-L78).
When `weighted_clauses=False`, those unit weights remain fixed. When it is true,
the model calls the weight bank after the clause feedback call.

[`WeightBank.c`](https://github.com/cair/tmu/blob/v0.8.3/tmu/lib/src/WeightBank.c#L35-L64)
shows that:

- only active, non-dropped clauses are eligible for increment or decrement;
- regression passes flags that permit increments but prevent decrements once a
  weight reaches one;
- weights therefore remain positive integers and cannot reach zero;
- no explicit positive upper bound is present in the inspected code.

“No explicit upper bound” means uncapped by this update rule, not mathematically
unbounded storage. TMU stores clause weights and the regression dot product in
signed 32-bit integers. A sufficiently long or extreme run could therefore
reach finite-range or overflow behaviour; neither the paper nor this review has
tested that boundary.

The P2 claim that an unwanted clause can be globally disabled with \(w=0\) does
not apply literally to TMU `v0.8.3`. A clause can still stop contributing on
particular inputs by learning literals that make its output zero.

TMU also separates the random decisions:

1. `clause_bank.type_i_feedback` or `type_ii_feedback` uses `update_p` to decide
   structure updates;
2. `weight_bank.increment` or `decrement` independently uses the same numerical
   `update_p` but performs its own random draw.

P2 Algorithm 1 expresses weight updates through the same \(p_j\) event used by
feedback. Therefore TMU follows the same broad idea but not the same
sample-by-sample stochastic coupling.

### 8.5 TMU `v0.8.3` CPU empty-clause asymmetry

The inspected CPU clause-bank paths do not treat a clause containing no included
literals identically during update and prediction:

- [`cb_calculate_clause_output_update`](https://github.com/cair/tmu/blob/v0.8.3/tmu/lib/src/ClauseBank.c#L199-L223)
  starts from output one and has no `all_exclude` suppression, so an empty clause
  can return one during the update calculation;
- [`cb_calculate_clause_output_predict`](https://github.com/cair/tmu/blob/v0.8.3/tmu/lib/src/ClauseBank.c#L247-L274)
  explicitly tracks `all_exclude` and only returns one when at least one literal
  is included.

This means that, on this CPU path, an empty clause can affect the training-side
vote, feedback branch, and weighted-clause eligibility while contributing zero
at prediction. This is an implementation observation, not a general property of
rTM. The actual backend used by the project must be probed because alternative
clause-bank implementations may differ.

### 8.6 TMU `v0.8.3` epoch, constant-target, and lifecycle semantics

One call to
[`TMRegressor.fit`](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/regression/vanilla_regressor.py#L84-L159)
performs one shuffled pass. It accepts unused `*args` and `**kwargs`; passing
`epochs=20` does not create 20 internal passes. The example correctly loops over
epochs and calls `fit` once per loop.

[`TMBaseModel.init`](https://github.com/cair/tmu/blob/v0.8.3/tmu/models/base.py#L210-L219)
runs only once per model instance. Consequently, the first call freezes the
target extrema, clause bank, and weight bank. Reusing one instance across folds,
different train splits, or supposedly independent seeds would continue the same
model and keep the first target scale. Every independent run or fold therefore
needs a new model object.

TMU explicitly encodes a constant training target as all zeros instead of
dividing by a zero target range. C1's inspected min–max path has no equivalent
constant-target guard. Constant-target behaviour is therefore another
version-specific edge case, not a paper-level rTM guarantee.

The supplied TMU example itself creates the model outside its repeated-run loop
and should not be copied as a rigorous repeated-split evaluation template.
No regressor-specific test was found in the pinned TMU `v0.8.3`
[`tests/` tree](https://github.com/cair/tmu/tree/v0.8.3/tests), which increases
the value of a project-owned parity fixture for these edge cases.

### 8.7 Consolidated comparison

| Mechanism | P1 journal definition | P2 RTM-IW definition | C1 original rTM | C2 pre-P2 code | TMU `v0.8.3` |
|---|---|---|---|---|---|
| Target mapping | Positive \(y_{\max}\) reference; no explicit affine \(y_{\min}\) equation | Normalised \(0\ldots1\) description | Affine min–max | Integer min–max to \(0\ldots T\) | Integer min–max to \(0\ldots T\) |
| Training vote clip | Not specified | Not specified | Yes | Yes | Yes |
| Inference vote clip | Says \(y_{\max}\) is not a hard bound | Not clear | Yes | Yes | No |
| Feedback probability | \(K|\hat y-y|/y_{\max}\) | \(|\hat y-y|/T\) in its notation | Linear absolute error/range | Squared encoded error | Squared encoded error |
| Weight initial value | Not applicable | 0 | Unit only | 1 | 1 |
| Minimum learned weight | Not applicable | 0 | Unit only | 1 | 1 |
| Structure/weight random event | Not applicable | Algorithm implies shared \(p_j\) | Not applicable | Shared mask | Separate draws |
| `fit` epoch meaning | Conceptual workflow | Conceptual workflow | Epoch loop inside call | Epoch loop inside call | One pass per call |
| Output beyond training maximum | Allowed by stated equation when votes exceed \(T\) | Formula permits it | Prevented | Prevented | Possible at inference |

The final implementation description in the dissertation must be based on the
code actually executed, not on one column selected for convenience.

## 9. Evidence from the four papers

### 9.1 P1 vanilla rTM

P1 uses two artificial datasets and five real-world datasets. The artificial
three-bit example shows how four, two, and one duplicate clauses can encode
binary place values. For most real tasks the authors use:

\[
m=2{,}000{,}000,\qquad T=1{,}000{,}000,
\]

and for dengue forecasting:

\[
m=200{,}000,\qquad T=100{,}000.
\]

The paper repeats the real-data comparisons 20 times and reports mean MAE with
95% confidence intervals. rTM is best among the reported RT, RF, and SVR
comparators on four of six targets, second on one, and third on one.

Useful conclusions:

- propositional clauses can serve as additive nonlinear regression components;
- large unweighted clause budgets can fit several tabular tasks;
- complete threshold encoding can represent ordered continuous features;
- clause count, resolution, and target scale are strongly coupled.

Limitations for this project:

- the practical unweighted model sizes are extremely large;
- training time, model memory, and energy are not reported;
- no modern boosting or neural baseline is included;
- no independent validation split is described for parameter search;
- “interpretability” on real tasks is asserted but real learned rule sets are not
  analysed in depth;
- extrapolation evidence comprises only 22 targets outside the training output
  range in one dataset;
- the Energy Performance task predicts building heating load from building
  attributes; it is not energy disaggregation or time-series NILM.

### 9.2 P2 integer-weighted rTM

P2 provides the central conceptual reason to test weighted rTM: it may allocate
clause count to **distinct patterns** and use integer weights for **pattern
magnitude**. It also demonstrates that the two are only partially decoupled:
more clauses can still learn overlapping patterns, and \(T\) still controls the
mapped unit scale and update dynamics.

Because the evidence is synthetic and does not report embedded cost, the safe
claim is:

> Integer weights can reduce the number of separate clauses required to
> represent repeated synthetic Boolean patterns.

The unsafe claim would be:

> `weighted_clauses=True` is already proved smaller, faster, and more accurate
> for NILM.

### 9.3 P3 C-RTM

P3 combines CTM-style moving image patches with rTM-style additive output. It
uses 72 artificial image datasets and reports competitive performance against
two simple CNN configurations. Its clearest contribution to this review is the
explicit pattern-allocation example: four pattern contributions of
\(8,4,2,1\) require 15 unit clauses.

It also shows a constructed case where using 16 instead of the required 15
clauses can lead to an incorrect allocation and output. This illustrates that a
unit-clause budget and \(T\) can interact with exact representability. It is not
a general rule that \(m\) must be a special multiple for real NILM.

C-RTM's convolution over image locations, filter coordinates, artificial masks,
and CNN comparisons do not transfer directly to a causal scalar power window.
The paper is supporting mechanism evidence only.

### 9.4 P4 energy forecasting

P4 uses Ausgrid data for one consumer. Its 12 features are described as
including year, week, weekday, weekend/holiday information, and energy use at
the corresponding time over the previous week. Data through week 24, reported
as 351 samples, form the training set; the rest form the test set. The exact
column construction, sampling unit, forecast horizon, target unit, and
Booleanisation are not specified well enough to reconstruct the dataset from
the paper alone.

The paper reports:

| Clauses | 10 | 50 | 100 | 200 | 500 | 1000 | 2000 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| MAE | 0.2352 | 0.2172 | 0.1983 | 0.1917 | **0.1840** | 0.2083 | 0.2360 |

At 500 clauses and 200 epochs it reports MAE 0.1840, compared with 0.2706,
0.2594, and 0.2599 for three simple ANN configurations.

What this supports:

- rTM has been applied to an energy-domain time-series forecasting task;
- history had to be supplied explicitly as features;
- more clauses did not monotonically improve the reported MAE.

What it does not support:

- 500 clauses being a general optimum;
- rTM being established as superior to modern forecasting methods;
- rTM being suitable for NILM;
- a leakage-controlled or cross-house evaluation;
- a reproducible implementation identity.

The study reports no validation set, no repeated seeds or uncertainty, no final
\(T\) or \(s\), only one consumer, 351 training samples, and only simple ANN
comparators. It states that \(T\) and \(s\) were selected by binary search but
does not state which data controlled that search. Because the reported
clause-count table also selects 500 clauses by test-set MAE with no validation
procedure described, apparent test-set model selection cannot be ruled out.

## 10. NILM relevance: supported properties and unresolved risks

### 10.1 Why the route is plausible

The following are reasonable motivations, not performance claims:

- appliance power is usually non-negative, matching the positive additive rTM
  form;
- many appliances contain repeated power platforms, transition patterns, or
  combinations that may be expressible by threshold clauses;
- the output remains numerical instead of treating neighbouring watt levels as
  unrelated classes;
- clauses can in principle be inspected as Boolean conditions over present and
  past aggregate-power features;
- weighted rTM may represent recurring platform magnitudes with fewer distinct
  clause structures than unit-weight rTM.

### 10.2 Output is quantised

Under TMU with training range
\([y_{\min},y_{\max}]\), one integer vote unit nominally corresponds to:

\[
\Delta y_{\mathrm{TMU}}
=\frac{y_{\max}-y_{\min}}{T}.
\tag{13}
\]

For a \(0\ldots2500\) W target and \(T=1000\), the nominal lattice spacing is
2.5 W. This is not the expected MAE. Several clauses may switch together,
target encoding is truncated, clauses can overlap, and the model may not learn
every reachable vote total.

### 10.3 Low-power feedback under TMU is a testable risk

With equation (7) and a \(0\ldots2500\) W target scale:

\[
p(20\text{ W error})
=
\left(\frac{20}{2500}\right)^2
=0.000064,
\]

or 0.0064% per eligible stochastic decision, while:

\[
p(500\text{ W error})
=
\left(\frac{500}{2500}\right)^2
=0.04.
\]

This supports the hypothesis that small absolute errors may receive much weaker
per-sample feedback than large errors in TMU. It does not prove that a 20 W
platform cannot be learned: the total effect also depends on how often the
sample occurs, epochs, number of clauses, active patterns, \(s\), target range,
and independent random updates.

### 10.4 OFF dominance is not solved by the mechanism definition

A full-stream appliance target may contain many exact zeros and few ON samples.
Possible outcomes include:

- an OFF sample predicted exactly at zero produces no error update;
- an OFF sample with positive prediction produces Type II feedback;
- frequent OFF samples may shape many clauses toward suppressing activation;
- ON errors are larger and may obtain stronger per-sample feedback;
- the balance among these effects is implementation- and distribution-dependent.

Therefore “rTM will collapse to zero” and “rTM inherently resists zero collapse”
are both premature. OFF proportion must be isolated in a mechanism experiment.

### 10.5 High-power spikes may dominate individual updates

A short 2000 W error in a 2500 W range gives a TMU update probability of 0.64,
far higher than the 20 W example. This creates a plausible risk that rare spikes
receive disproportionately strong per-occurrence updates. Frequency may still
counterbalance magnitude. Spike duration, sample weighting, target scaling, and
clipping must be examined rather than assumed.

### 10.6 Learned clauses are readable rules, not automatically causal explanations

A clause such as:

\[
P_t>1000
\land
\Delta P_t>500
\land
P_{t-3}<200
\]

can be read as a logical condition. It does not follow that:

- the rule is stable across seeds or houses;
- every included literal is physically meaningful;
- the clause identifies the true appliance mechanism;
- the complete weighted sum is simple enough for a human to audit;
- a post-event or future feature is causal merely because the rule is readable.

Interpretability evaluation should include clause duplication, literal count,
stability, weight concentration, and timing provenance, not only one example
rule.

## 11. cTM–rTM is a candidate architecture, not a literature result

The four rTM papers do not evaluate a classification-TM gate followed by an rTM
for NILM. Any such structure is a project hypothesis.

### 11.1 Candidate forms

| Candidate | Description | Potential advantage | Main risk |
|---|---|---|---|
| Direct rTM | Train one rTM per appliance on the full target including OFF | Simplest end-to-end numerical model | OFF imbalance and global target range may dominate |
| Oracle-gated rTM | Use true ON/OFF labels as the gate and evaluate conditional regression | Diagnostic upper bound on the value of perfect gating | Label-assisted/oracle only; not deployable evidence |
| Learned cTM–rTM | cTM estimates gate \(\hat g_t\); rTM estimates conditional power \(\hat r_t\) | Separates state detection from conditional magnitude; ON-only target range may be narrower | Gate errors propagate directly; two models increase cost |
| Multi-state cTM plus conditional values | cTM predicts OFF/low/high or appliance states, with one value or regressor per state | May isolate multi-platform appliances | State definitions and boundaries may be arbitrary or appliance-specific |

A hard-gated output would be:

\[
\hat P_t=\hat g_t\hat r_t,\qquad \hat g_t\in\{0,1\}.
\tag{14}
\]

A false negative from the gate forces predicted power to zero regardless of rTM
quality. A false positive exposes the conditional rTM output during true OFF.
The final system must therefore be evaluated on the combined \(\hat P_t\), not
only by reporting gate F1 and conditional ON-sample MAE separately.

### 11.2 Why ON-only rTM training could change the dynamics

If rTM is fitted only on ON samples, TMU's \(y_{\min}\) may become the lowest ON
power rather than zero. This can:

- narrow the target range;
- increase the relative feedback assigned to a given watt error;
- map zero votes to \(y_{\min,\mathrm{ON}}\), which is sensible only after a
  correct gate.

These are mechanism inferences. They do not establish that ON-only training is
better. Low-power standby states, uncertain state labels, transitional samples,
and false-positive gates may make the conditional target definition difficult.

### 11.3 Required fairness for a later comparison

Direct rTM, oracle-gated rTM, and learned cTM–rTM should share:

- the same development samples and causal input availability;
- training-only threshold and scaler fitting;
- the same appliance target and evaluation period;
- the same target clipping policy at scoring;
- declared and comparable parameter/resource budgets;
- the same seed/fold plan.

The oracle variant must remain labelled oracle and must not select the final
test method through candidate-test feedback.

## 12. Programming guidance derived from the review

These are implementation constraints for a future authorised task, not a frozen
design.

### 12.1 Pin and record the executed implementation

Every run should record:

- installed package version;
- public tag/commit used as reference;
- hash of the installed Python regressor source;
- hash or build identity of the compiled TMU library;
- Python, NumPy, compiler, and platform versions;
- all constructor parameters and the caller's epoch loop.

The public `v0.8.3` source is not proof of the wheel installed on Tianhang's
Windows environment. Source parity must be checked locally before a paper claim
about TMU behaviour.

### 12.2 Treat preprocessing as part of the model

The saved model bundle will need, at minimum:

- ordered raw feature schema and units;
- causal timing/window definition;
- Boolean threshold values and bit orientation;
- feature-negation setting;
- \(y_{\min}\), \(y_{\max}\), and target dtype/rounding rule;
- clause count, \(T\), \(s\), TA-state configuration, and weight mode;
- output clipping or non-clipping policy.

Validation/test data must never refit thresholds, ranges, state labels, or
appliance thresholds.

### 12.3 Wrap TMU's epoch semantics explicitly

Project code should expose an unambiguous operation such as `fit_one_epoch` or
implement its own visible epoch loop. It should not pass `epochs=N` into TMU
`v0.8.3` and assume the keyword is honoured.

Each independent seed, fold, appliance, and parameter setting needs a fresh
`TMRegressor` instance. Reusing the object would also reuse clause state, weights,
and the first target range.

### 12.4 Preserve internal observables

A mechanism/debug path should be able to retain:

- original watt target;
- integer encoded target \(z\);
- raw vote \(V\);
- training-clipped vote \(\tilde V\);
- inverse-mapped raw prediction;
- any explicitly clipped reporting prediction;
- clause outputs or active-clause count;
- learned weight distribution;
- number of zero, unit, and larger weights where the implementation permits
  them;
- literal count and exact/near-duplicate clause summaries;
- per-epoch error and update counts.

If the current API does not expose an item, the report should mark it unavailable
or justify an instrumented experimental copy. It must not reconstruct hidden
state from final MAE alone.

### 12.5 Do not hide clipping

At least three distinct quantities may exist:

1. raw TMU inference output;
2. physically clipped output, for example to non-negative power or a declared
   appliance limit;
3. the output actually scored and deployed.

Any clip should be a named decision and reported as a post-processing condition.
Raw and clipped metrics should be retained during diagnostics. Silent clipping
would hide the exact source behaviour and make paper/code comparison
impossible.

### 12.6 Do not assume classifier deployment parity

The current project classifier path exports class clauses and votes. An rTM
also needs target range, vote-to-watt arithmetic, and possibly integer clause
weights with sufficient accumulator width. Before Pico work, the following need
separate verification:

- weight representation and maximum observed value;
- accumulator overflow bound;
- integer/fixed-point inverse scaling;
- raw-versus-clipped prediction convention;
- Python/host/Pico parity fixtures;
- model bytes, flash, RAM, and latency.

## 13. Proposed mechanism checks before REDD

These are successor recommendations. They do not allocate an E-series ID or
authorise execution.

| Check | Minimal construction | Required observations | What it resolves |
|---|---|---|---|
| Source parity | Compare local installed wheel files and compiled library against fixed public source | versions, hashes, code paths | Whether TMU `v0.8.3` findings describe the actual environment |
| Output lattice | One- or two-bit inputs with hand-computable targets and small \(m,T\) | encoded target, raw vote, clipped train vote, predicted value | Target rounding and watts-per-vote |
| Train/predict clipping | Force or inject \(V>T\) | train error, raw inference, inverse output | Whether maximum-target overshoot is visible to training |
| Epoch semantics | Compare one call with an `epochs` keyword against repeated calls | state/weight hash and prediction after each pass | Exact caller contract |
| Weight boundary | Weighted model on a repeatedly overpredicted active clause | initial and minimum weights | Whether local implementation reaches zero |
| Random coupling | Instrument structure and weight update events | per-clause update event pairs | Whether local build uses independent draws |
| Duplicate-pattern compression | P2's 2–4 bit functions, fixed data and seeds | exact clauses, near-duplicates, weights, MAE, state bytes, operation count | What “compact” means in the executed implementation |
| Low/high error scale | Same pattern with 20 W and 500 W errors under one target range | update counts and convergence by error level | Whether squared feedback suppresses low-power learning in practice |
| OFF proportion | Fixed ON patterns with controlled OFF ratios | ON/OFF MAE, update counts, false positive power | Effect of zero dominance |
| Spike frequency | Fixed platform plus controlled rare high spikes | platform/spike MAE and update allocation | Magnitude–frequency competition |
| Target-range shift | Same central data with and without a training-only extreme | target encoding, feedback, MAE by platform | Sensitivity to \(y_{\max}\) |
| Clause stability | Repeat identical setup across declared seeds | rule overlap, weight rank, literal stability | Whether readable rules are stable enough to analyse |

Each mechanism question should change one main variable. A large sweep that
changes weighting, target range, window, Booleanisation, and gating together
would not reveal which mechanism caused the result.

## 14. Provisional path to a NILM development experiment

Only after the source and artificial checks should an authorised development
experiment consider REDD. A defensible sequence would be:

1. freeze a causal input/target definition and development-only data scope;
2. fit Boolean thresholds and target scaling on training data only;
3. establish a simple direct vanilla-rTM route;
4. change only `weighted_clauses` for the first structural comparison;
5. inspect output range, platform-specific error, clause duplication, weights,
   and resource cost, not only global MAE;
6. introduce oracle gating only as a diagnostic;
7. test a learned cTM gate only if the diagnostic indicates that separating
   state and conditional power is useful.

Useful development evidence may include:

- overall MAE and median absolute error;
- per-appliance and per-power-state MAE;
- OFF false-positive watt distribution;
- ON underestimation and missed-energy contribution;
- energy-total error over declared intervals;
- state precision/recall/F1 under a threshold fixed from training/validation;
- raw output overflow frequency and magnitude;
- seed/fold mean, sample standard deviation, and paired differences;
- clause count, TA state count, literal count, weight distribution, model bytes,
  and inference time.

The exact metrics and acceptance rules require a frozen experiment design. This
review does not add them to Protocol R.

The current formal baseline is event-level classification. A causal
sample-by-sample rTM target, a paired-event energy target, and a conditional
ON-state power target are different research tasks. A successor must select one
explicitly rather than calling all of them “rTM NILM”.

## 15. Dissertation value

### 15.1 Material already suitable for a literature/mechanism section

The following points are supported with citations:

- rTM replaces class-polarity voting with additive clause contributions for
  positive regression;
- continuous features can be represented by cumulative Boolean thresholds;
- \(T\) sets a nominal output scale, while \(m\) controls clause capacity and,
  for unit weights, vote coverage;
- Type I and Type II feedback are selected according to under- and
  overprediction;
- RTM-IW interprets a non-negative integer weight as repeated copies of one
  pattern;
- rTM has been evaluated on tabular regression and one energy-forecasting task;
- public implementations differ materially from the paper definitions.

### 15.2 Material that requires experiments before dissertation use as a result

- rTM improves NILM power estimation;
- weighted rTM is more compact on Pico;
- low-power phases are suppressed by TMU feedback;
- output overshoot materially affects REDD;
- cTM gating improves combined power estimates;
- learned clauses correspond to physically meaningful appliance states;
- any specific \(m,T,s\), threshold count, window, or clipping policy is best.

### 15.3 Likely discussion and limitation material

Even a negative rTM result could be valuable if the experiment isolates:

- squared-error feedback versus appliance power range;
- OFF/ON imbalance;
- rare spike versus frequent low-power platforms;
- clause duplication versus learned integer weights;
- raw output extrapolation versus physical clipping;
- accuracy–model-size–latency trade-offs.

Those mechanisms would explain why an approach was retained, modified, or
rejected rather than presenting development as blind parameter search.

## 16. Open items and revision triggers

| Open item | Why it matters | Evidence that should close it |
|---|---|---|
| Local TMU package/source parity | Public tag behaviour may not match Tianhang's installed wheel | local file and compiled-library hashes plus import/version record |
| Exact empty-clause semantics in update and predict modes | Can change initial votes and OFF behaviour | fixed-input mechanism trace |
| TA state-bit effect in TMU rTM | Affects learning inertia and memory | source trace plus isolated state-bit comparison |
| Raw vote access | Required to diagnose clipping and overflow | supported API or instrumented local experimental copy |
| Weight/TA serialisation | Required for reproducible models and later export | save/reload parity test |
| Output clipping policy | Changes metrics and physical plausibility | predeclared raw/clipped comparison |
| Direct versus ON-only target | Changes range, OFF handling, and gate dependence | controlled direct/oracle-gated comparison |
| Causal window definition | Supplies all temporal information to rTM | declared dependency horizon and boundary-reset tests |
| Interpretability method | Clause readability alone is insufficient | rule extraction, duplication, stability, and timing audit |
| Pico representation | Weighted accumulation may change width and cost | host-native/Pico design and parity measurements |

## 17. Recommendations

1. Treat broad rTM literature discovery as sufficient for the present mechanism
   stage. Further progress should come from fixed-source verification and small
   mechanism experiments.
2. Use TMU `v0.8.3` only with an explicit adapter and recorded version identity;
   do not describe it as a literal implementation of P1 or P2.
3. Compare vanilla and weighted modes on the same artificial data and fixed
   conditions before using REDD.
4. Preserve raw votes, clipped votes, encoded targets, weights, and clause
   statistics from the start; adding observability after a failed NILM run would
   require repeating the work.
5. Keep direct rTM, oracle gating, and learned cTM–rTM as separate candidates.
   Do not promote gating because it sounds structurally reasonable.
6. Continue to protect the Protocol R candidate-test boundary. All rTM
   feasibility work should remain development-only until a formal method and
   evaluation contract are authorised.

## References

1. K. D. Abeyrathna, O.-C. Granmo, X. Zhang, L. Jiao, and M. Goodwin,
   “The regression Tsetlin machine: a novel approach to interpretable nonlinear
   regression,” *Philosophical Transactions of the Royal Society A*, vol. 378,
   issue 2164, art. 20190165, 2020.
   [DOI](https://doi.org/10.1098/rsta.2019.0165)
2. K. D. Abeyrathna, O.-C. Granmo, and M. Goodwin, “A Regression Tsetlin
   Machine with Integer Weighted Clauses for Compact Pattern Representation,”
   arXiv:2002.01245v1, 2020. [arXiv](https://arxiv.org/abs/2002.01245)
   The later conference chapter is titled “Integer Weighted Regression Tsetlin
   Machines.” [DOI](https://doi.org/10.1007/978-3-030-55789-8_59)
3. K. D. Abeyrathna, O.-C. Granmo, and M. Goodwin, “Convolutional Regression
   Tsetlin Machine: An Interpretable Approach to Convolutional Regression,”
   *ICMLT 2021*, pp. 65–73, 2021.
   [DOI](https://doi.org/10.1145/3468891.3468901)
4. S. N. Ranasinghe and H. S. G. Pussewalage, “Short-term Energy Forecasting
   using the Regression Tsetlin Machine,” *UCC 2023*, 2023.
   [DOI](https://doi.org/10.1145/3603166.3632543)
5. `cair/regression-tsetlin-machine`, commit
   `f65f8a093f474bdfaa3b019450318fe960b522f5`.
   [Repository snapshot](https://github.com/cair/regression-tsetlin-machine/tree/f65f8a093f474bdfaa3b019450318fe960b522f5)
6. `cair/pyTsetlinMachine`, commit
   `079a09327b4d566d2f27b66db9b5893493c0e549`.
   [Repository snapshot](https://github.com/cair/pyTsetlinMachine/tree/079a09327b4d566d2f27b66db9b5893493c0e549)
7. `cair/tmu`, tag `v0.8.3`, commit
   `df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483`.
   [Repository snapshot](https://github.com/cair/tmu/tree/df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483)

## Revision record

| Date | Change | Evidence status |
|---|---|---|
| 2026-07-24 | Initial detailed review from four supplied papers and three pinned public source snapshots | Literature and public-source review complete; no local wheel parity or mechanism experiment |
