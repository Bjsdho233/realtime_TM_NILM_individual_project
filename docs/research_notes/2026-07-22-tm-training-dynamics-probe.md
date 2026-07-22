# TM Training-Dynamics Probe

An unnumbered exploratory probe was run on 2026-07-22 after the minimum Han reproduction. It examined training order, class sampling, the TM threshold `T`, and hard-negative multiclass feedback while holding the matched events, 23-slot feature vector, 184-bit Booleanisation, model shape, and inference representation fixed.

The archived evidence is in [`experiments/2026-07-22-tm-training-dynamics-probe`](../../experiments/2026-07-22-tm-training-dynamics-probe/README.md).

The probe's main finding is that the original appliance-blocked online training order should not remain the comparison baseline. Shuffling every original event once per epoch increased five-seed H3 Macro F1 from `0.4809 +/- 0.0210` to `0.5288 +/- 0.0097`, with all five paired seed labels higher. Accuracy decreased from `0.7868` to `0.7640`.

`T=10`, hard-negative feedback, and global class balancing were not supported as default improvements. Partial balance at `alpha=0.5` improved mean dishwasher F1 but did not exceed unique shuffle in Macro F1 or accuracy.

These are diagnostic Protocol H-style results only. H3 was viewed repeatedly, the class set includes `electric furnace`, event generation is label-assisted, and the features are not causal. The archive does not advance Protocol R, adopt a new model, or authorise later implementation work.
