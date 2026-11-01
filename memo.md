# Replication memo: "Wired for Change? How Democratic Diasporas Undermine Autocracies"

**To:** Nilou Davis, Frida Lopez-Bravo, Izzy Sunby  **Cc:** Gov 2020 instructors  **From:** Haonan Tian

Thanks for a very clean replication package. It ran with one command, and your `expected_output/` folder made it easy to check my results. Below are some suggestions, starting with the most important. My code is in `code/` if you want to rerun anything.

## 1. Did it replicate?

Yes. All your results tables came out exactly the same, and Figures 1–4 match the draft.

**One exception:** the figure comparing rich democracies, poor democracies and rich autocracies doesn't match your code. The draft shows rich democracies at +0.9 and remittances going *up*. Your current code gives rich democracies about +0.1 (not significant), poor democracies +0.7, and remittances going slightly *down*. It may be from an older version of the code. Please regenerate it, because the two versions lead to different conclusions.

Also, please remove the file `country_converter.py` from your zip. It's an offline stand-in for the real package, and it assigns some wrong country codes, which changes some results.

## 2. Suggestions

**(1) The abstract says the opposite of the results.** The abstract says the *wealth* of host countries matters more than their *democracy*. Your Results section, and your code, say democracy matters more. The abstract also mentions Facebook data, which the paper doesn't use. Easy fix: rewrite the abstract at the end, once the results are final.

**(2) The country fixed-effects sentence needs a small correction.** The draft says the results come from changes *within* countries over time and disappear with fixed effects. It's actually the reverse: when an effect disappears after adding country fixed effects, it means the result comes from comparing *different countries* with each other. Each country's diaspora changes very slowly, so there is little within-country change to learn from. That's not fatal, but say it clearly.

**(3) Your "instability" result is really a "democratization" result, which is good news for you.** Your instability measure counts any big change, up or down. When I split it, all of the effect comes from countries becoming *more* democratic, and none from becoming *less* democratic. I also checked whether countries with democratic diasporas were already democratizing *before* (in the previous 5 years). They weren't. Both checks support your story, and "democratization" matches your new research question better than "instability".

**(4) You can test your Wealth vs. Democracy hypotheses directly.** Your data already has a measure of how *rich* the countries where emigrants live are. If you put it in the same regression as the democracy measure, democracy stays significant and wealth doesn't. You worried that the two are too closely related to separate, but in your sample they're only weakly related (correlation 0.25), so you *can* separate them. This is a simpler and stronger test than the bar-chart figure.

**(5) Be careful how you describe the telecom result.** "Not significant" doesn't always mean "no effect". Sometimes the data just can't tell. For democratization, your data can rule out a large telecom effect. For the other outcomes the uncertainty is too big to say much. Also, you measure telecom only in the *home* country, but your idea is about the *connection* between emigrants and home. A better measure would be something like international phone call volume.

**(6) Tell a positive story.** Instead of "telecom doesn't matter", try: "Democratic diasporas push autocracies toward democracy, but not through phone lines or money. So what carries the effect?" That makes the null results interesting, and points to ideas and norms that migrants bring back (sometimes called "social remittances"). Also mention that your data ends in 2005, before smartphones and social media. Extending it to recent years is a natural next step.

## 3. Who would care about this paper

- Scholars of democratization and migration
- People debating whether the internet helps or hurts dictatorships
- Policy organizations that support diaspora activists (like the Freedom House report you cite)

## 4. Other things you could check or mention

- Larger diasporas should have bigger effects.
- Free speech in host countries might matter more than wealth (this variable is already in your data, and it does seem to matter).
- Dictatorships facing democratic diasporas might deliberately limit phone and internet access. Your own results hint at this.
- Future work: protests at home, or surveys of people with relatives abroad.

**Small bug:** country code 347 (Yugoslavia/Serbia) is being matched to Kosovo by mistake. Adding `347: "SRB"` to the `manual` list in the code fixes it. The results barely change.

Looking forward to the revision!
